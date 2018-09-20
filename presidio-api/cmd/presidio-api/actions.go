package main

import (
	"fmt"
	"net/http"

	"github.com/gin-gonic/gin"

	types "github.com/Microsoft/presidio-genproto/golang"
	services "github.com/Microsoft/presidio/pkg/presidio"
	server "github.com/Microsoft/presidio/pkg/server"
	templates "github.com/Microsoft/presidio/pkg/templates"
)

var analyzeService *types.AnalyzeServiceClient
var anonymizeService *types.AnonymizeServiceClient
var schedulerService *types.SchedulerServiceClient

func setupGRPCServices() {
	analyzeService = services.SetupAnalyzerService()
	anonymizeService = services.SetupAnonymizerService()
	schedulerService = services.SetupSchedulerService()
}

func (api *API) analyze(c *gin.Context) {
	var analyzeAPIRequest types.AnalyzeApiRequest

	if c.Bind(&analyzeAPIRequest) == nil {
		analyzeTemplate := api.getAnalyzeTemplate(analyzeAPIRequest.AnalyzeTemplateId, analyzeAPIRequest.AnalyzeTemplate, c.Param("project"), c)
		if analyzeTemplate == nil {
			return
		}

		res := api.invokeAnalyze(analyzeTemplate, analyzeAPIRequest.Text, c)
		if res == nil {
			return
		}
		server.WriteResponse(c, http.StatusOK, res)
	}
}

func (api *API) anonymize(c *gin.Context) {
	var anonymizeAPIRequest types.AnonymizeApiRequest

	if c.Bind(&anonymizeAPIRequest) == nil {
		project := c.Param("project")

		analyzeTemplate := api.getAnalyzeTemplate(anonymizeAPIRequest.AnalyzeTemplateId, anonymizeAPIRequest.AnalyzeTemplate, project, c)
		if analyzeTemplate == nil {
			return
		}

		anonymizeTemplate := api.getAnonymizeTemplate(anonymizeAPIRequest.AnonymizeTemplateId, anonymizeAPIRequest.AnonymizeTemplate, project, c)
		if anonymizeTemplate == nil {
			return
		}

		analyzeRes := api.invokeAnalyze(analyzeTemplate, anonymizeAPIRequest.Text, c)
		if analyzeRes == nil {
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
	var cronAPIJobRequest types.ScannerCronJobApiRequest

	if c.Bind(&cronAPIJobRequest) == nil {
		project := c.Param("project")
		scannerCronJobRequest := api.getScannerCronJobRequest(&cronAPIJobRequest, project, c)
		scheulderResponse := api.invokeScannerCronJobScheduler(scannerCronJobRequest, c)
		if scheulderResponse == nil {
			return
		}

		server.WriteResponse(c, http.StatusOK, scheulderResponse)
	}
}

func (api *API) invokeScannerCronJobScheduler(scannerCronJobRequest *types.ScannerCronJobRequest, c *gin.Context) *types.ScannerCronJobResponse {
	srv := *schedulerService
	res, err := srv.ApplyScan(c, scannerCronJobRequest)
	if err != nil {
		c.AbortWithError(http.StatusInternalServerError, err)
		return nil
	}
	return res
}

func (api *API) getScannerCronJobRequest(cronJobAPIRequest *types.ScannerCronJobApiRequest, project string, c *gin.Context) *types.ScannerCronJobRequest {
	scanRequest := &types.ScanRequest{}
	trigger := &types.Trigger{}
	var name string

	if cronJobAPIRequest.ScannerCronJobTemplateId != "" {
		cronJobTemplate := &types.ScannerCronJobTemplate{}
		api.getTemplate(project, scheduleScannerCronJob, cronJobAPIRequest.ScannerCronJobTemplateId, cronJobTemplate, c)

		scanID := cronJobTemplate.ScanTemplateId
		scanTemplate := &types.ScanTemplate{}
		api.getTemplate(project, scan, scanID, scanTemplate, c)

		datasinkTemplate := &types.DatasinkTemplate{}
		api.getTemplate(project, datasink, cronJobTemplate.DatasinkTemplateId, datasinkTemplate, c)

		analyzeTemplate := &types.AnalyzeTemplate{}
		api.getTemplate(project, analyze, cronJobTemplate.AnalyzeTemplateId, analyzeTemplate, c)

		anonymizeTemplate := &types.AnonymizeTemplate{}
		if cronJobTemplate.AnonymizeTemplateId != "" {
			api.getTemplate(project, anonymize, cronJobTemplate.AnonymizeTemplateId, anonymizeTemplate, c)
		}
		trigger = cronJobTemplate.GetTrigger()
		name = cronJobTemplate.GetName()
		scanRequest = &types.ScanRequest{
			AnalyzeTemplate:   analyzeTemplate,
			AnonymizeTemplate: anonymizeTemplate,
			DatasinkTemplate:  datasinkTemplate,
			ScanTemplate:      scanTemplate,
		}
	} else if cronJobAPIRequest.ScannerCronJobRequest != nil {
		scanRequest = cronJobAPIRequest.ScannerCronJobRequest.GetScanRequest()
		trigger = cronJobAPIRequest.ScannerCronJobRequest.GetTrigger()
		name = cronJobAPIRequest.ScannerCronJobRequest.GetName()
	} else {
		c.AbortWithError(http.StatusBadRequest, fmt.Errorf("ScannerCronJobTemplateId or ScannerCronJobRequest must be supplied"))
		return nil
	}

	return &types.ScannerCronJobRequest{
		Trigger:     trigger,
		ScanRequest: scanRequest,
		Name:        name,
	}
}

func (api *API) scheduleStreamsJob(c *gin.Context) {
	var streamsJobRequest types.StreamsJobApiRequest

	if c.Bind(&streamsJobRequest) == nil {
		project := c.Param("project")
		streamsJobRequest := api.getStreamsJobRequest(&streamsJobRequest, project, c)
		scheulderResponse := api.invokeStreamsJobScheduler(streamsJobRequest, project, c)
		if scheulderResponse == nil {
			return
		}

		server.WriteResponse(c, http.StatusOK, scheulderResponse)
	}
}

func (api *API) invokeStreamsJobScheduler(streamsJobRequest *types.StreamsJobRequest, project string, c *gin.Context) *types.StreamsJobResponse {
	srv := *schedulerService
	res, err := srv.ApplyStream(c, streamsJobRequest)
	if err != nil {
		c.AbortWithError(http.StatusInternalServerError, err)
		return nil
	}
	return res
}

func (api *API) getStreamsJobRequest(jobAPIRequest *types.StreamsJobApiRequest, project string, c *gin.Context) *types.StreamsJobRequest {
	streamsJobRequest := &types.StreamsJobRequest{}

	if jobAPIRequest.GetStreamsJobTemplateId() != "" {
		jobTemplate := &types.StreamsJobTemplate{}
		api.getTemplate(project, scheduleStreamsJob, jobAPIRequest.StreamsJobTemplateId, jobTemplate, c)

		streamID := jobTemplate.GetStreamsTemplateId()
		streamTemplate := &types.StreamTemplate{}
		api.getTemplate(project, stream, streamID, streamTemplate, c)

		datasinkTemplate := &types.DatasinkTemplate{}
		api.getTemplate(project, datasink, jobTemplate.GetDatasinkTemplateId(), datasinkTemplate, c)

		analyzeTemplate := &types.AnalyzeTemplate{}
		api.getTemplate(project, analyze, jobTemplate.GetAnalyzeTemplateId(), analyzeTemplate, c)

		anonymizeTemplate := &types.AnonymizeTemplate{}
		if jobTemplate.AnonymizeTemplateId != "" {
			api.getTemplate(project, anonymize, jobTemplate.GetAnonymizeTemplateId(), anonymizeTemplate, c)
		}
		streamsJobRequest = &types.StreamsJobRequest{
			Name: streamTemplate.GetName(),
			StreamsRequest: &types.StreamRequest{
				AnalyzeTemplate:   analyzeTemplate,
				AnonymizeTemplate: anonymizeTemplate,
				DatasinkTemplate:  datasinkTemplate,
				StreamConfig:      streamTemplate.GetStreamConfig(),
			},
		}
	} else if jobAPIRequest.GetStreamsJobRequest() != nil {
		streamsJobRequest = jobAPIRequest.GetStreamsJobRequest()
	} else {
		c.AbortWithError(http.StatusBadRequest, fmt.Errorf("StreamsJobTemplateId or StreamsRequest must be supplied"))
		return nil
	}

	return streamsJobRequest
}

func (api *API) invokeAnonymize(anonymizeTemplate *types.AnonymizeTemplate, text string, results []*types.AnalyzeResult, c *gin.Context) *types.AnonymizeResponse {
	srv := *anonymizeService

	request := &types.AnonymizeRequest{
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

func (api *API) invokeAnalyze(analyzeTemplate *types.AnalyzeTemplate, text string, c *gin.Context) *types.AnalyzeResponse {
	analyzeRequest := &types.AnalyzeRequest{
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

func (api *API) getAnalyzeTemplate(analyzeTemplateID string, analyzeTemplate *types.AnalyzeTemplate,
	project string, c *gin.Context) *types.AnalyzeTemplate {

	if analyzeTemplate == nil && analyzeTemplateID != "" {
		analyzeTemplate = &types.AnalyzeTemplate{}
		api.getTemplate(project, analyze, analyzeTemplateID, analyzeTemplate, c)
	} else if analyzeTemplate == nil {
		c.AbortWithError(http.StatusBadRequest, fmt.Errorf("AnalyzeTemplate or AnalyzeTemplateId must be supplied"))
		return nil
	}

	return analyzeTemplate
}

func (api *API) getAnonymizeTemplate(anonymizeTemplateID string, anonymizeTemplate *types.AnonymizeTemplate,
	project string, c *gin.Context) *types.AnonymizeTemplate {

	if anonymizeTemplate == nil && anonymizeTemplateID != "" {
		anonymizeTemplate = &types.AnonymizeTemplate{}
		api.getTemplate(project, anonymize, anonymizeTemplateID, anonymizeTemplate, c)
	} else if anonymizeTemplate == nil {
		c.AbortWithError(http.StatusBadRequest, fmt.Errorf("AnalyzeTemplate or AnalyzeTemplateId must be supplied"))
		return nil
	}

	return anonymizeTemplate
}
