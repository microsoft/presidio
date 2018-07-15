package main

import (
	"fmt"

	"errors"
	"net/http"

	"github.com/gin-gonic/gin"

	message_types "github.com/presid-io/presidio-genproto/golang"
	helper "github.com/presid-io/presidio/pkg/helper"
	server "github.com/presid-io/presidio/pkg/server"
	pkg_templates "github.com/presid-io/presidio/pkg/templates"
)

func getFieldTypes(c *gin.Context) {
	result, _ := pkg_templates.GetFieldTypes()
	server.WriteResponse(c, http.StatusOK, result)
}

func (api *API) getActionTemplate(c *gin.Context) {
	action := c.Param("action")
	project := c.Param("project")
	id := c.Param("id")
	key := pkg_templates.CreateKey(project, action, id)
	result, err := api.templates.GetTemplate(key)
	if err != nil {
		server.WriteResponse(c, http.StatusBadRequest, fmt.Sprintf("Failed to retrieve template %s %q", key, err))
		return
	}
	server.WriteResponse(c, http.StatusOK, result)
}

func (api *API) postActionTemplate(c *gin.Context) {
	action := c.Param("action")
	project := c.Param("project")
	id := c.Param("id")
	value, err := validateTemplate(action, c)
	if err != nil {
		server.WriteResponse(c, http.StatusBadRequest, fmt.Sprintf("Failed to add template %q", err))
		return
	}
	err = api.templates.InsertTemplate(project, action, id, value)
	if err != nil {
		server.WriteResponse(c, http.StatusBadRequest, fmt.Sprintf("Failed to add template %q", err))
		return
	}
	server.WriteResponse(c, http.StatusCreated, "Template added successfully ")
}

func (api *API) putActionTemplate(c *gin.Context) {
	action := c.Param("action")
	project := c.Param("project")
	id := c.Param("id")
	value, err := validateTemplate(action, c)
	if err != nil {
		server.WriteResponse(c, http.StatusBadRequest, fmt.Sprintf("Failed to update template %q", err))
		return
	}
	err = api.templates.UpdateTemplate(project, action, id, value)
	if err != nil {
		server.WriteResponse(c, http.StatusBadRequest, fmt.Sprintf("Failed to update template %q", err))
	}

	server.WriteResponse(c, http.StatusOK, "Template updated successfully")
}

func (api *API) deleteActionTemplate(c *gin.Context) {
	action := c.Param("action")
	project := c.Param("project")
	id := c.Param("id")
	err := api.templates.DeleteTemplate(project, action, id)
	if err != nil {
		server.WriteResponse(c, http.StatusBadRequest, fmt.Sprintf("Failed to delete template %q", err))
		return
	}
	server.WriteResponse(c, http.StatusNoContent, "")
}

//TODO: Need to better validate templates
func validateTemplate(action string, c *gin.Context) (string, error) {
	switch action {
	case "analyze":
		var analyzerTemplate message_types.AnalyzeRequest
		if c.BindJSON(&analyzerTemplate) == nil {
			return helper.ConvertInterfaceToJSON(analyzerTemplate)
		}
	case "anonymize":
		var anonymizeTemplate message_types.AnonymizeTemplate
		if c.BindJSON(&anonymizeTemplate) == nil {
			return helper.ConvertInterfaceToJSON(anonymizeTemplate)
		}
	}

	return "", errors.New("No template found")
}
