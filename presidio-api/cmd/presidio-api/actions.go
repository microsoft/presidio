package main

import (
	"fmt"
	"net/http"

	"github.com/gin-gonic/gin"

	types "github.com/Microsoft/presidio-genproto/golang"
	"github.com/Microsoft/presidio/pkg/presidio"
	server "github.com/Microsoft/presidio/pkg/server"
)

const maxImageSize = 4194304

func (api *API) setupGRPCServices() {
	api.Services.SetupAnalyzerService()
	api.Services.SetupAnonymizerService()
	api.Services.SetupAnonymizerImageService()
	api.Services.SetupSchedulerService()
	api.Services.SetupOCRService()
}

func (api *API) analyze(c *gin.Context) {
	var analyzeAPIRequest types.AnalyzeApiRequest

	if c.Bind(&analyzeAPIRequest) == nil {
		analyzeTemplate := api.getAnalyzeTemplate(analyzeAPIRequest.AnalyzeTemplateId, analyzeAPIRequest.AnalyzeTemplate, c.Param("project"), c)
		if analyzeTemplate == nil {
			return
		}

		res, err := api.Services.AnalyzeItem(c, analyzeAPIRequest.Text, analyzeTemplate)
		if err != nil {
			c.AbortWithError(http.StatusInternalServerError, err)
			return
		}
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

		analyzeRes, err := api.Services.AnalyzeItem(c, anonymizeAPIRequest.Text, analyzeTemplate)
		if err != nil {
			c.AbortWithError(http.StatusInternalServerError, err)
			return
		}
		if analyzeRes == nil {
			return
		}

		anonymizeRes, err := api.Services.AnonymizeItem(c, analyzeRes, anonymizeAPIRequest.Text, anonymizeTemplate)
		if err != nil {
			c.AbortWithError(http.StatusInternalServerError, err)
			return
		}
		if anonymizeRes == nil {
			return
		}
		server.WriteResponse(c, http.StatusOK, anonymizeRes)
	}
}

func (api *API) anonymizeImage(c *gin.Context) {
	var anonymizeImageAPIRequest types.AnonymizeImageApiRequest

	project := c.Param("project")

	anonymizeImageAPIRequest.ImageType = c.PostForm("imageType")
	if anonymizeImageAPIRequest.ImageType == "" {
		c.AbortWithError(http.StatusBadRequest, fmt.Errorf("Image type is missing (image/jpeg, image/png, image/tiff, image/gif, image/bmp)"))
		return
	}

	presidio.ConvertJSONToInterface(c.PostForm("anonymizeImageTemplate"), &anonymizeImageAPIRequest.AnonymizeImageTemplate)
	anonymizeImageTemplate := api.getAnonymizeImageTemplate(anonymizeImageAPIRequest.AnonymizeImageTemplateId, anonymizeImageAPIRequest.AnonymizeImageTemplate, project, c)
	if anonymizeImageTemplate == nil {
		return
	}

	image := &types.Image{
		Data: getImageFile(c),
	}

	if image.Data == nil {
		return
	}

	if anonymizeImageAPIRequest.DetectionType == types.DetectionTypeEnum_OCR {

		presidio.ConvertJSONToInterface(c.PostForm("analyzeTemplate"), &anonymizeImageAPIRequest.AnalyzeTemplate)
		analyzeTemplate := api.getAnalyzeTemplate(anonymizeImageAPIRequest.AnalyzeTemplateId, anonymizeImageAPIRequest.AnalyzeTemplate, project, c)
		if analyzeTemplate == nil {
			return
		}

		analyzeResults := api.applyPresidioOCR(c, image, analyzeTemplate)
		image.ImageType = anonymizeImageAPIRequest.ImageType
		anonymizeResult, err := api.Services.AnonymizeImageItem(c, image, analyzeResults, anonymizeImageAPIRequest.DetectionType, anonymizeImageTemplate)
		if err != nil {
			c.AbortWithError(http.StatusInternalServerError, err)
			return
		}
		c.Data(http.StatusOK, anonymizeImageAPIRequest.ImageType, anonymizeResult.Image.Data)
	}
}

func (api *API) applyPresidioOCR(c *gin.Context, image *types.Image, analyzeTemplate *types.AnalyzeTemplate) []*types.AnalyzeResult {
	ocrRes, err := api.Services.OcrItem(c, image)
	if err != nil {
		c.AbortWithError(http.StatusInternalServerError, err)
		return nil
	}
	if ocrRes.Image.Text == "" {
		c.AbortWithError(http.StatusNoContent, fmt.Errorf("No content found in image"))

		return nil
	}

	image.Text = ocrRes.Image.Text
	image.Boundingboxes = ocrRes.Image.Boundingboxes

	analyzeResults, err := api.Services.AnalyzeItem(c, ocrRes.Image.Text, analyzeTemplate)
	if err != nil {
		c.AbortWithError(http.StatusInternalServerError, err)
		return nil
	}
	if analyzeResults == nil {
		c.AbortWithError(http.StatusNoContent, fmt.Errorf("No content found in image"))
		return nil
	}
	return analyzeResults
}

func getImageFile(c *gin.Context) []byte {
	fileh, err := c.FormFile("data")
	if err != nil {
		c.AbortWithError(http.StatusBadRequest, err)
		return nil
	}
	if fileh.Size >= maxImageSize {
		c.AbortWithError(http.StatusBadRequest, fmt.Errorf("File size is over 4MB"))
		return nil
	}

	file, err := fileh.Open()
	if err != nil {
		c.AbortWithError(http.StatusBadRequest, err)
		return nil
	}

	bt := make([]byte, fileh.Size)
	_, err = file.Read(bt)
	if err != nil {
		c.AbortWithError(http.StatusBadRequest, err)
		return nil
	}
	err = file.Close()
	if err != nil {
		c.AbortWithError(http.StatusBadRequest, err)
		return nil
	}
	return bt
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

	res, err := api.Services.ApplyScan(c, scannerCronJobRequest)
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
		scheulderResponse := api.invokeStreamsJobScheduler(streamsJobRequest, c)
		if scheulderResponse == nil {
			return
		}

		server.WriteResponse(c, http.StatusOK, scheulderResponse)
	}
}

func (api *API) invokeStreamsJobScheduler(streamsJobRequest *types.StreamsJobRequest, c *gin.Context) *types.StreamsJobResponse {
	res, err := api.Services.ApplyStream(c, streamsJobRequest)
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

func (api *API) getTemplate(project string, action string, id string, obj interface{}, c *gin.Context) {
	template, err := api.Templates.GetTemplate(project, action, id)
	if err != nil {
		c.AbortWithError(http.StatusBadRequest, err)
	}
	err = presidio.ConvertJSONToInterface(template, obj)
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
		c.AbortWithError(http.StatusBadRequest, fmt.Errorf("AnonymizeTemplate or AnonymizeTemplateId must be supplied"))
		return nil
	}

	return anonymizeTemplate
}

func (api *API) getAnonymizeImageTemplate(anonymizeImageTemplateID string, anonymizeImageTemplate *types.AnonymizeImageTemplate,
	project string, c *gin.Context) *types.AnonymizeImageTemplate {

	if anonymizeImageTemplate == nil && anonymizeImageTemplateID != "" {
		anonymizeImageTemplate = &types.AnonymizeImageTemplate{}
		api.getTemplate(project, anonymizeImage, anonymizeImageTemplateID, anonymizeImageTemplate, c)
	} else if anonymizeImageTemplate == nil {
		c.AbortWithError(http.StatusBadRequest, fmt.Errorf("AnonymizeImageTemplate or AnonymizeImageTemplateId must be supplied"))
		return nil
	}

	return anonymizeImageTemplate
}
