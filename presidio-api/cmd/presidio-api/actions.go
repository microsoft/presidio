package main

import (
	"fmt"
	"net/http"
	"os"

	"github.com/gin-gonic/gin"

	log "github.com/presid-io/presidio/pkg/logger"
	"github.com/presid-io/presidio/pkg/rpc"

	message_types "github.com/presid-io/presidio-genproto/golang"
	server "github.com/presid-io/presidio/pkg/server"
	templates "github.com/presid-io/presidio/pkg/templates"
)

var analyzeService *message_types.AnalyzeServiceClient
var anonymizeService *message_types.AnonymizeServiceClient
var jobService *message_types.JobServiceClient

func setupGRPCServices() {
	var err error

	analyzerSvcHost := os.Getenv("ANALYZER_SVC_HOST")
	if analyzerSvcHost == "" {
		log.Fatal("analyzer service address is empty")
	}

	analyzerSvcPort := os.Getenv("ANALYZER_SVC_PORT")
	if analyzerSvcPort == "" {
		log.Fatal("analyzer service port is empty")
	}

	anonymizerSvcHost := os.Getenv("ANONYMIZER_SVC_HOST")
	if anonymizerSvcHost == "" {
		log.Fatal("anonymizer service address is empty")
	}

	anonymizerSvcPort := os.Getenv("ANONYMIZER_SVC_PORT")
	if anonymizerSvcPort == "" {
		log.Fatal("anonymizer service port is empty")
	}

	analyzeService, err = rpc.SetupAnalyzerService(analyzerSvcHost + ":" + analyzerSvcPort)
	if err != nil {
		log.Error(fmt.Sprintf("Connection to analyzer service failed %q", err))
	}
	anonymizeService, err = rpc.SetupAnonymizeService(anonymizerSvcHost + ":" + anonymizerSvcPort)
	if err != nil {
		log.Error(fmt.Sprintf("Connection to anonymizer service failed %q", err))
	}

}

func (api *API) analyze(c *gin.Context) {
	var analyzeAPIRequest message_types.AnalyzeApiRequest

	if c.Bind(&analyzeAPIRequest) == nil {
		id := analyzeAPIRequest.AnalyzeTemplateId
		project := c.Param("project")
		res := api.invokeAnalyze(project, id, analyzeAPIRequest.Text, c)
		if res == nil {
			return
		}
		server.WriteResponse(c, http.StatusOK, res)
	}
}

func (api *API) anonymize(c *gin.Context) {
	var anonymizeAPIRequest message_types.AnonymizeApiRequest

	if c.Bind(&anonymizeAPIRequest) == nil {

		id := anonymizeAPIRequest.AnalyzeTemplateId
		project := c.Param("project")
		analyzeRes := api.invokeAnalyze(project, id, anonymizeAPIRequest.Text, c)
		if analyzeRes == nil {
			return
		}

		id = anonymizeAPIRequest.AnonymizeTemplateId
		anonymizeRes := api.invokeAnonymize(project, id, anonymizeAPIRequest.Text, analyzeRes.AnalyzeResults, c)
		if anonymizeRes == nil {
			return
		}
		server.WriteResponse(c, http.StatusOK, anonymizeRes)
	}
}

func (api *API) schedule(c *gin.Context) {
	var jobTemplate message_types.JobTemplate

	if c.Bind(&jobTemplate) == nil {
		project := c.Param("project")
		scheulderResponse := api.invokeJobScheduler(jobTemplate, project, c)
		if scheulderResponse == nil {
			return
		}

		server.WriteResponse(c, http.StatusOK, scheulderResponse)
	}
}

func (api *API) invokeJobScheduler(jobTemplate message_types.JobTemplate, project string,  c *gin.Context) *message_types.JobResponse {
	scanId := jobTemplate.ScanTemplateId
	scanTemplate := &message_types.ScanTemplate{}
	api.getTemplate(project, "scan", scanId, scanTemplate, c)

	databinderTemplate := &message_types.DatabinderTemplate{}
	api.getTemplate(project, "databinder", scanTemplate.DatabinderTemplateId, databinderTemplate, c)

	analyzeTemplate := &message_types.AnalyzeTemplate{}
	api.getTemplate(project, "analyze", scanTemplate.AnalyzeTemplateId, analyzeTemplate, c)

	anonymizeTemplate := &message_types.AnonymizeTemplate{}
	if scanTemplate.AnonymizeTemplateId != "" {
		api.getTemplate(project, "anonymize", scanTemplate.AnonymizeTemplateId, anonymizeTemplate, c)
	}

	scanRequest := &message_types.ScanRequest{
		AnalyzeTemplate: analyzeTemplate,
		AnonymizeTemplate: anonymizeTemplate,
		DatabinderTemplate: databinderTemplate,
		InputConfig: scanTemplate.InputConfig,
		Kind: scanTemplate.Kind,
		MinProbability: scanTemplate.MinProbability,
	}

	request := &message_types.JobRequest{
		Name: jobTemplate.Name,
		Description: jobTemplate.Description,
		Trigger: jobTemplate.Trigger,
		ScanRequest: scanRequest
	}
	srv := *jobService
	res, err := srv.Apply(c, request)
	if err != nil {
		c.AbortWithError(http.StatusInternalServerError, err)
		return nil
	}
	return res
}

func (api *API) invokeAnonymize(project string, id string, text string, results []*message_types.AnalyzeResult, c *gin.Context) *message_types.AnonymizeResponse {
	anonymizeKey := templates.CreateKey(project, "anonymize", id)
	result, err := api.templates.GetTemplate(anonymizeKey)

	if err != nil {
		c.AbortWithError(http.StatusBadRequest, err)
		return nil
	}
	srv := *anonymizeService
	anonymizeTemplate := &message_types.AnonymizeTemplate{}
	err = templates.ConvertJSONToInterface(result, anonymizeTemplate)
	if err != nil {
		c.AbortWithError(http.StatusBadRequest, err)
		return nil
	}
	request := &message_types.AnonymizeRequest{
		Template:       anonymizeTemplate,
		Text:           text,
		AnalyzeResults: results,
	}
	res, err := srv.Apply(c, request)
	if err != nil {
		c.AbortWithError(http.StatusInternalServerError, err)
		return nil
	}
	return res
}

func (api *API) invokeAnalyze(project string, id string, text string, c *gin.Context) *message_types.AnalyzeResponse {
	analyzeKey := templates.CreateKey(project, "analyze", id)
	analyzeRequest, err := getAnalyzeRequest(api.templates, analyzeKey)

	if err != nil {
		c.AbortWithError(http.StatusBadRequest, err)
		return nil
	}

	analyzeRequest.Text = text

	srv := *analyzeService
	analyzeResponse, err := srv.Apply(c, analyzeRequest)
	if err != nil {
		c.AbortWithError(http.StatusInternalServerError, err)
		return nil
	}

	return analyzeResponse
}

func getAnalyzeRequest(apiTemplates *templates.Templates, analyzeKey string) (*message_types.AnalyzeRequest, error) {
	template, err := apiTemplates.GetTemplate(analyzeKey)

	if err != nil {
		return nil, fmt.Errorf("Failed to retrieve template %q", err)
	}

	analyzeTemplate := &message_types.AnalyzeTemplate{}
	err = templates.ConvertJSONToInterface(template, analyzeTemplate)
	if err != nil {
		return nil, fmt.Errorf("Failed to convert template %q", err)
	}
	analyzeRequest := &message_types.AnalyzeRequest{
		AnalyzeTemplate: analyzeTemplate,
	}

	return analyzeRequest, nil
}

func (api *API) getTemplate(project string, action string, id string, obj interface{}, c *gin.Context) {
	key := templates.CreateKey(project, action, id)
	template, err := api.templates.GetTemplate(key)
	if err != nil {
		c.AbortWithError(http.StatusBadRequest, err)
	}
	err = templates.ConvertJSONToInterface(template, obj)
	if err != nil {
		c.AbortWithError(http.StatusBadRequest, err)
	}
}
