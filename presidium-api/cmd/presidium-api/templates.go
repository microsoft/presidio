package main

import (
	"fmt"

	"encoding/json"
	"errors"
	"net/http"

	"github.com/gin-gonic/gin"

	server "github.com/presidium-io/presidium/pkg/server"
	message_types "github.com/presidium-io/presidium/pkg/types"
)

func getFieldTypes(c *gin.Context) {
	result, _ := convertInterface2Json(message_types.FieldTypes)
	server.WriteResponse(c, http.StatusOK, result)
}

func createKey(project string, action string, id string) string {
	key := fmt.Sprintf("%s/%s/%s", project, action, id)
	return key
}

func (api API) getTemplate(project string, action string, id string) (string, error) {
	key := createKey(project, action, id)
	return api.kvStore.GetKVPair(key)
}

func (api API) insertTemplate(project string, action string, id string, value string) error {
	key := createKey(project, action, id)
	return api.kvStore.PutKVPair(key, value)
}

func (api API) updateTemplate(project string, action string, id string, value string) error {
	key := createKey(project, action, id)
	err := api.kvStore.DeleteKVPair(key)
	if err != nil {
		return err
	}
	return api.kvStore.PutKVPair(key, value)
}

func (api API) deleteTemplate(project string, action string, id string) error {
	key := createKey(project, action, id)
	return api.kvStore.DeleteKVPair(key)
}

func (api API) getActionTemplate(c *gin.Context) {
	action := c.Param("action")
	project := c.Param("project")
	id := c.Param("id")
	result, err := api.getTemplate(project, action, id)
	if err != nil {
		server.WriteResponse(c, http.StatusBadRequest, fmt.Sprintf("Failed to retrieve template %q", err))
		return
	}
	server.WriteResponse(c, http.StatusOK, result)
}

func (api API) postActionTemplate(c *gin.Context) {
	action := c.Param("action")
	project := c.Param("project")
	id := c.Param("id")
	value, err := validateTemplate(action, c)
	if err != nil {
		server.WriteResponse(c, http.StatusBadRequest, fmt.Sprintf("Failed to add template %q", err))
		return
	}
	err = api.insertTemplate(project, action, id, value)
	if err != nil {
		server.WriteResponse(c, http.StatusBadRequest, fmt.Sprintf("Failed to add template %q", err))
		return
	}
	server.WriteResponse(c, http.StatusOK, "Template added successfully")
}

func (api API) patchActionTemplate(c *gin.Context) {
	action := c.Param("action")
	project := c.Param("project")
	id := c.Param("id")
	value, err := validateTemplate(action, c)
	if err != nil {
		server.WriteResponse(c, http.StatusBadRequest, fmt.Sprintf("Failed to update template %q", err))
		return
	}
	err = api.updateTemplate(project, action, id, value)
	if err != nil {
		server.WriteResponse(c, http.StatusBadRequest, fmt.Sprintf("Failed to update template %q", err))
	}

	server.WriteResponse(c, http.StatusOK, "Template updated successfully")
}

func (api API) deleteActionTemplate(c *gin.Context) {
	action := c.Param("action")
	project := c.Param("project")
	id := c.Param("id")
	err := api.deleteTemplate(project, action, id)
	if err != nil {
		server.WriteResponse(c, http.StatusBadRequest, fmt.Sprintf("Failed to delete template %q", err))
		return
	}
	server.WriteResponse(c, http.StatusOK, "Template deleted successfully")
}

//TODO: Need to better validate templates
func validateTemplate(action string, c *gin.Context) (string, error) {
	switch action {
	case "analyze":
		var analyzerTemplate message_types.AnalyzeRequest
		if c.BindJSON(&analyzerTemplate) == nil {
			return convertInterface2Json(analyzerTemplate)
		}
	case "anonymize":
		var anonymizeTemplate message_types.AnonymizeTemplate
		if c.BindJSON(&anonymizeTemplate) == nil {
			return convertInterface2Json(anonymizeTemplate)
		}
	}

	return "", errors.New("No template found")
}

func convertInterface2Json(template interface{}) (string, error) {
	b, err := json.Marshal(template)
	if err != nil {
		return "", err
	}
	return string(b), nil
}

func convertJSON2Interface(template string, convertTo interface{}) error {
	err := json.Unmarshal([]byte(template), &convertTo)
	return err
}
