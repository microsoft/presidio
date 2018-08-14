package main

import (
	"fmt"
	"net/http"

	"github.com/gin-gonic/gin"

	message_types "github.com/Microsoft/presidio-genproto/golang"
	services "github.com/Microsoft/presidio/pkg/presidio"
	server "github.com/Microsoft/presidio/pkg/server"
	templates "github.com/Microsoft/presidio/pkg/templates"
)

var analyzeService *message_types.AnalyzeServiceClient
var anonymizeService *message_types.AnonymizeServiceClient
var schedulerService *message_types.SchedulerServiceClient

func setupGRPCServices() {
	analyzeService = services.SetupAnalyzerService()
	anonymizeService = services.SetupAnoymizerService()
	schedulerService = services.SetupSchedulerService()
}

func (api *API) analyze(c *gin.Context) {
	var analyzeAPIRequest message_types.AnalyzeApiRequest

	if c.Bind(&analyzeAPIRequest) == nil {
		analyzeTemplate := analyzeAPIRequest.AnalyzeTemplate

		if analyzeTemplate == nil && analyzeAPIRequest.AnalyzeTemplateId != "" {
			analyzeTemplate = &message_types.AnalyzeTemplate{}
			api.getTemplate(c.Param("project"), "analyze", analyzeAPIRequest.AnalyzeTemplateId, analyzeTemplate, c)
		} else if analyzeTemplate == nil {
			c.AbortWithError(http.StatusBadRequest, fmt.Errorf("AnalyzeTemplate or AnalyzeTemplateId must be supplied"))
			return
		}

		res := api.invokeAnalyze(analyzeTemplate, analyzeAPIRequest.Text, c)
		if res == nil {
			return
		}
		server.WriteResponse(c, http.StatusOK, res)
	}
}

func isTemplateIDInitialized(template *message_types.AnalyzeTemplate, templateID string) bool {
	return template == nil && templateID != ""
}

func (api *API) anonymize(c *gin.Context) {
	var anonymizeAPIRequest message_types.AnonymizeApiRequest

	if c.Bind(&anonymizeAPIRequest) == nil {
		var err error
		analyzeTemplate := anonymizeAPIRequest.AnalyzeTemplate
		id := anonymizeAPIRequest.AnalyzeTemplateId
		project := c.Param("project")

		if isTemplateIDInitialized(analyzeTemplate, anonymizeAPIRequest.AnalyzeTemplateId) {
			analyzeTemplate = &message_types.AnalyzeTemplate{}
			api.getTemplate(project, "analyze", id, analyzeTemplate, c)
		} else if analyzeTemplate == nil {
			c.AbortWithError(http.StatusBadRequest, fmt.Errorf("AnalyzeTemplate or AnalyzeTemplateId must be supplied"))
			return
		}

		analyzeRes := api.invokeAnalyze(analyzeTemplate, anonymizeAPIRequest.Text, c)
		if analyzeRes == nil {
			return
		}

		anonymizeTemplate := anonymizeAPIRequest.AnonymizeTemplate
		if anonymizeTemplate == nil && anonymizeAPIRequest.AnonymizeTemplateId != "" {
			id = anonymizeAPIRequest.AnonymizeTemplateId
			anonymizeTemplate = &message_types.AnonymizeTemplate{}
			api.getTemplate(project, "anonymize", id, anonymizeTemplate, c)
			if err != nil {
				c.AbortWithError(http.StatusBadRequest, err)
			}
		} else if anonymizeTemplate == nil {
			c.AbortWithError(http.StatusBadRequest, fmt.Errorf("AnalyzeTemplate or AnalyzeTemplateId must be supplied"))
			return
		}

		anonymizeRes := api.invokeAnonymize(anonymizeTemplate, anonymizeAPIRequest.Text, analyzeRes.AnalyzeResults, c)
		if anonymizeRes == nil {
			return
		}
		server.WriteResponse(c, http.StatusOK, anonymizeRes)
	}
}

func (api *API) scheduleScannerCronJob(c *gin.Context) {
	var cronAPIJobRequest message_types.ScannerCronJobApiRequest

	if c.Bind(&cronAPIJobRequest) == nil {
		project := c.Param("project")
		scheulderResponse := api.invokeScannerCronJobScheduler(cronAPIJobRequest, project, c)
		if scheulderResponse == nil {
			return
		}

		server.WriteResponse(c, http.StatusOK, scheulderResponse)
	}
}

func (api *API) invokeScannerCronJobScheduler(cronJobAPIRequest message_types.ScannerCronJobApiRequest, project string, c *gin.Context) *message_types.ScannerCronJobResponse {
	cronJobTemplate := &message_types.ScannerCronJobTemplate{}
	api.getTemplate(project, "schedule-scanner-cronjob", cronJobAPIRequest.ScannerCronJobTemplateId, cronJobTemplate, c)

	scanID := cronJobTemplate.ScanTemplateId
	scanTemplate := &message_types.ScanTemplate{}
	api.getTemplate(project, "scan", scanID, scanTemplate, c)

	datasinkTemplate := &message_types.DatasinkTemplate{}
	api.getTemplate(project, "datasink", cronJobTemplate.DatasinkTemplateId, datasinkTemplate, c)

	analyzeTemplate := &message_types.AnalyzeTemplate{}
	api.getTemplate(project, "analyze", cronJobTemplate.AnalyzeTemplateId, analyzeTemplate, c)

	anonymizeTemplate := &message_types.AnonymizeTemplate{}
	if cronJobTemplate.AnonymizeTemplateId != "" {
		api.getTemplate(project, "anonymize", cronJobTemplate.AnonymizeTemplateId, anonymizeTemplate, c)
	}

	scanRequest := &message_types.ScanRequest{
		AnalyzeTemplate:    analyzeTemplate,
		AnonymizeTemplate:  anonymizeTemplate,
		DatasinkTemplate:   datasinkTemplate,
		CloudStorageConfig: scanTemplate.GetCloudStorageConfig(),
		Kind:               scanTemplate.GetKind(),
		MinProbability:     scanTemplate.GetMinProbability(),
	}

	request := &message_types.ScannerCronJobRequest{
		Description: cronJobTemplate.Description,
		Trigger:     cronJobTemplate.Trigger,
		ScanRequest: scanRequest,
	}
	srv := *schedulerService
	res, err := srv.ApplyScan(c, request)
	if err != nil {
		c.AbortWithError(http.StatusInternalServerError, err)
		return nil
	}
	return res
}

func (api *API) scheduleStreamsJob(c *gin.Context) {
	var streamsJobRequest message_types.StreamsJobApiRequest

	if c.Bind(&streamsJobRequest) == nil {
		project := c.Param("project")
		scheulderResponse := api.invokeStreamsJobScheduler(streamsJobRequest, project, c)
		if scheulderResponse == nil {
			return
		}

		server.WriteResponse(c, http.StatusOK, scheulderResponse)
	}
}

func (api *API) invokeStreamsJobScheduler(jobAPIRequest message_types.StreamsJobApiRequest, project string, c *gin.Context) *message_types.StreamsJobResponse {
	jobTemplate := &message_types.StreamsJobTemplate{}
	api.getTemplate(project, "schedule-scanner-cronjob", jobAPIRequest.StreamsJobTemplateId, jobTemplate, c)

	streamID := jobTemplate.StreamsTemplateId
	streamTemplate := &message_types.StreamTemplate{}
	api.getTemplate(project, "stream", streamID, streamTemplate, c)

	datasinkTemplate := &message_types.DatasinkTemplate{}
	api.getTemplate(project, "datasink", jobTemplate.DatasinkTemplateId, datasinkTemplate, c)

	analyzeTemplate := &message_types.AnalyzeTemplate{}
	api.getTemplate(project, "analyze", jobTemplate.AnalyzeTemplateId, analyzeTemplate, c)

	anonymizeTemplate := &message_types.AnonymizeTemplate{}
	if jobTemplate.AnonymizeTemplateId != "" {
		api.getTemplate(project, "anonymize", jobTemplate.AnonymizeTemplateId, anonymizeTemplate, c)
	}

	streamsRequest := &message_types.StreamRequest{
		AnalyzeTemplate:   analyzeTemplate,
		AnonymizeTemplate: anonymizeTemplate,
		DatasinkTemplate:  datasinkTemplate,
		StreamConfig:      streamTemplate.GetStreamConfig(),
		Kind:              streamTemplate.GetKind(),
		MinProbability:    streamTemplate.GetMinProbability(),
	}

	request := &message_types.StreamsJobRequest{
		Description:    jobTemplate.Description,
		StreamsRequest: streamsRequest,
	}
	srv := *schedulerService
	res, err := srv.ApplyStream(c, request)
	if err != nil {
		c.AbortWithError(http.StatusInternalServerError, err)
		return nil
	}
	return res
}

func (api *API) invokeAnonymize(anonymizeTemplate *message_types.AnonymizeTemplate, text string, results []*message_types.AnalyzeResult, c *gin.Context) *message_types.AnonymizeResponse {
	srv := *anonymizeService

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

func (api *API) invokeAnalyze(analyzeTemplate *message_types.AnalyzeTemplate, text string, c *gin.Context) *message_types.AnalyzeResponse {
	analyzeRequest := &message_types.AnalyzeRequest{
		AnalyzeTemplate: analyzeTemplate,
		Text:            text,
	}

	srv := *analyzeService
	analyzeResponse, err := srv.Apply(c, analyzeRequest)
	if err != nil {
		c.AbortWithError(http.StatusInternalServerError, err)
		return nil
	}

	return analyzeResponse
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
