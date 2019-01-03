package main

import (
	"fmt"
	"net/http"

	"github.com/gin-gonic/gin"

	types "github.com/Microsoft/presidio-genproto/golang"
	"github.com/Microsoft/presidio/pkg/presidio"
	server "github.com/Microsoft/presidio/pkg/server"
)

func getFieldTypes(c *gin.Context) {
	var fieldTypeArray []types.FieldTypes
	for key := range types.FieldTypesEnum_value {
		fieldTypeArray = append(fieldTypeArray, types.FieldTypes{Name: key})
	}
	server.WriteResponse(c, http.StatusOK, fieldTypeArray)
}

func (api *API) getActionTemplate(c *gin.Context) {
	action := c.Param("action")
	project := c.Param("project")
	id := c.Param("id")
	result, err := api.Templates.GetTemplate(project, action, id)
	if err != nil {
		server.AbortWithError(c, http.StatusBadRequest, err)
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
		server.AbortWithError(c, http.StatusBadRequest, err)
		return
	}
	err = api.Templates.InsertTemplate(project, action, id, value)
	if err != nil {
		server.AbortWithError(c, http.StatusBadRequest, err)
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
		server.AbortWithError(c, http.StatusBadRequest, err)
		return
	}
	err = api.Templates.UpdateTemplate(project, action, id, value)
	if err != nil {
		server.AbortWithError(c, http.StatusBadRequest, err)
		return
	}

	server.WriteResponse(c, http.StatusOK, "Template updated successfully")
}

func (api *API) deleteActionTemplate(c *gin.Context) {
	action := c.Param("action")
	project := c.Param("project")
	id := c.Param("id")
	err := api.Templates.DeleteTemplate(project, action, id)
	if err != nil {
		server.AbortWithError(c, http.StatusBadRequest, err)
		return
	}
	server.WriteResponse(c, http.StatusNoContent, "")
}

//TODO: Need to better validate templates
func validateTemplate(action string, c *gin.Context) (string, error) {
	switch action {
	case analyze:
		var analyzerTemplate types.AnalyzeTemplate
		return bindAndConvert(analyzerTemplate, c)
	case anonymize:
		var anonymizeTemplate types.AnonymizeTemplate
		return bindAndConvert(anonymizeTemplate, c)
	case scan:
		var scanTemplate types.ScanTemplate
		return bindAndConvert(scanTemplate, c)
	case datasink:
		var datasinkTemplate types.DatasinkTemplate
		return bindAndConvert(datasinkTemplate, c)
	case scheduleScannerCronJob:
		var scannerCronjobTemplate types.ScannerCronJobTemplate
		return bindAndConvert(scannerCronjobTemplate, c)
	case scheduleStreamsJob:
		var streamsJobTemplate types.StreamsJobTemplate
		return bindAndConvert(streamsJobTemplate, c)
	}

	return "", fmt.Errorf("No template found")
}

func bindAndConvert(template interface{}, c *gin.Context) (string, error) {
	if c.BindJSON(&template) == nil {
		return presidio.ConvertInterfaceToJSON(template)
	}
	return "", fmt.Errorf("No template found")
}
