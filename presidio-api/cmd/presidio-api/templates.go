package main

import (
	"errors"
	"net/http"

	"github.com/gin-gonic/gin"

	message_types "github.com/Microsoft/presidio-genproto/golang"
	server "github.com/Microsoft/presidio/pkg/server"
	pkg_templates "github.com/Microsoft/presidio/pkg/templates"
)

func getFieldTypes(c *gin.Context) {
	var fieldTypeArray []message_types.FieldTypes
	for key := range message_types.FieldTypesEnum_value {
		fieldTypeArray = append(fieldTypeArray, message_types.FieldTypes{Name: key})
	}
	server.WriteResponse(c, http.StatusOK, fieldTypeArray)
}

func (api *API) getActionTemplate(c *gin.Context) {
	action := c.Param("action")
	project := c.Param("project")
	id := c.Param("id")
	key := pkg_templates.CreateKey(project, action, id)
	result, err := api.templates.GetTemplate(key)
	if err != nil {
		c.AbortWithError(http.StatusBadRequest, err)
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
		c.AbortWithError(http.StatusBadRequest, err)
		return
	}
	err = api.templates.InsertTemplate(project, action, id, value)
	if err != nil {
		c.AbortWithError(http.StatusBadRequest, err)
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
		c.AbortWithError(http.StatusBadRequest, err)
		return
	}
	err = api.templates.UpdateTemplate(project, action, id, value)
	if err != nil {
		c.AbortWithError(http.StatusBadRequest, err)
	}

	server.WriteResponse(c, http.StatusOK, "Template updated successfully")
}

func (api *API) deleteActionTemplate(c *gin.Context) {
	action := c.Param("action")
	project := c.Param("project")
	id := c.Param("id")
	err := api.templates.DeleteTemplate(project, action, id)
	if err != nil {
		c.AbortWithError(http.StatusBadRequest, err)
		return
	}
	server.WriteResponse(c, http.StatusNoContent, "")
}

//TODO: Need to better validate templates
func validateTemplate(action string, c *gin.Context) (string, error) {
	switch action {
	case "analyze":
		var analyzerTemplate message_types.AnalyzeTemplate
		return bindAndConvert(analyzerTemplate, c)
	case "anonymize":
		var anonymizeTemplate message_types.AnonymizeTemplate
		return bindAndConvert(anonymizeTemplate, c)
	case "scan":
		var scanTemplate message_types.ScanTemplate
		return bindAndConvert(scanTemplate, c)
	case "datasink":
		var datasinkTemplate message_types.DatasinkTemplate
		return bindAndConvert(datasinkTemplate, c)
	case "schedule-scanner-cronjob":
		var scannerCronjobTemplate message_types.ScannerCronJobTemplate
		return bindAndConvert(scannerCronjobTemplate, c)
	case "schedule-streams-job":
		var streamsJobTemplate message_types.StreamsJobTemplate
		return bindAndConvert(streamsJobTemplate, c)
	}

	return "", errors.New("No template found")
}

func bindAndConvert(template interface{}, c *gin.Context) (string, error) {
	if c.BindJSON(&template) == nil {
		return pkg_templates.ConvertInterfaceToJSON(template)
	}
	return "", errors.New("No template found")
}
