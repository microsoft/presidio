package main

import (
	"fmt"
	"mime/multipart"
	"net/http"

	"github.com/gin-gonic/gin"

	types "github.com/Microsoft/presidio-genproto/golang"
	"github.com/Microsoft/presidio/pkg/presidio"
	server "github.com/Microsoft/presidio/pkg/server"
	store "github.com/Microsoft/presidio/presidio-api/cmd/presidio-api/api"
	"github.com/Microsoft/presidio/presidio-api/cmd/presidio-api/api/analyze"
	"github.com/Microsoft/presidio/presidio-api/cmd/presidio-api/api/anonymize"
	ai "github.com/Microsoft/presidio/presidio-api/cmd/presidio-api/api/anonymize-image"
	"github.com/Microsoft/presidio/presidio-api/cmd/presidio-api/api/recognizers"
	scj "github.com/Microsoft/presidio/presidio-api/cmd/presidio-api/api/scanner-cron-job"
	sj "github.com/Microsoft/presidio/presidio-api/cmd/presidio-api/api/stream-job"
	"github.com/Microsoft/presidio/presidio-api/cmd/presidio-api/api/templates"
)

func getFieldTypes(c *gin.Context) {
	t := templates.GetFieldTypes()
	server.WriteResponse(c, http.StatusOK, t)

}

func getActionTemplate(c *gin.Context) {
	action := c.Param("action")
	project := c.Param("project")
	id := c.Param("id")
	result, err := templates.GetActionTemplate(api, project, action, id)
	if err != nil {
		server.AbortWithError(c, http.StatusBadRequest, err)
		return

	}
	server.WriteResponse(c, http.StatusOK, result)
}

func postActionTemplate(c *gin.Context) {
	action := c.Param("action")
	project := c.Param("project")
	id := c.Param("id")
	value, err := validateTemplate(action, c)
	if err != nil {
		server.AbortWithError(c, http.StatusBadRequest, err)
		return
	}
	result, err := templates.PostActionTemplate(api, project, action, id, value)
	if err != nil {
		server.AbortWithError(c, http.StatusBadRequest, err)
		return
	}
	server.WriteResponse(c, http.StatusOK, result)
}

func putActionTemplate(c *gin.Context) {
	action := c.Param("action")
	project := c.Param("project")
	id := c.Param("id")
	value, err := validateTemplate(action, c)
	if err != nil {
		server.AbortWithError(c, http.StatusBadRequest, err)
		return
	}
	result, err := templates.PutActionTemplate(api, project, action, id, value)
	if err != nil {
		server.AbortWithError(c, http.StatusBadRequest, err)
		return
	}
	server.WriteResponse(c, http.StatusOK, result)
}

func deleteActionTemplate(c *gin.Context) {
	action := c.Param("action")
	project := c.Param("project")
	id := c.Param("id")
	result, err := templates.DeleteActionTemplate(api, project, action, id)
	if err != nil {
		server.AbortWithError(c, http.StatusBadRequest, err)
		return

	}
	server.WriteResponse(c, http.StatusOK, result)
}

func analyzeText(c *gin.Context) {
	var analyzeAPIRequest *types.AnalyzeApiRequest
	project := c.Param("project")
	if c.Bind(&analyzeAPIRequest) == nil {
		result, err := analyze.Analyze(c, api, analyzeAPIRequest, project)
		if err != nil {
			server.AbortWithError(c, http.StatusBadRequest, err)
			return
		}
		server.WriteResponseWithRequestID(
			c,
			http.StatusOK,
			result.RequestId,
			result.AnalyzeResults)
	}
}

func anonymizeText(c *gin.Context) {
	var anonymizeAPIRequest *types.AnonymizeApiRequest
	project := c.Param("project")
	if c.Bind(&anonymizeAPIRequest) == nil {
		result, err := anonymize.Anonymize(c, api, anonymizeAPIRequest, project)
		if err != nil {
			server.AbortWithError(c, http.StatusBadRequest, err)
			return
		}
		server.WriteResponse(c, http.StatusOK, result)
	}
}

func anonymizeImage(c *gin.Context) {

	project := c.Param("project")

	anonymizeImageAPIRequest, err := bindAnonymizeImageParameters(c)
	if err != nil {
		server.AbortWithError(c, http.StatusBadRequest, err)
		return
	}

	result, err := ai.AnonymizeImage(c, api, anonymizeImageAPIRequest, project)
	if err != nil {
		server.AbortWithError(c, http.StatusBadRequest, err)
		return
	}
	c.Data(http.StatusOK, anonymizeImageAPIRequest.ImageType, result)
}

func bindAnonymizeImageParameters(c *gin.Context) (*types.AnonymizeImageApiRequest, error) {
	anonymizeImageAPIRequest := &types.AnonymizeImageApiRequest{}

	anonymizeImageAPIRequest.ImageType, _ = c.GetPostForm("imageType")

	anonymizeImageTemplate, _ := c.GetPostForm("anonymizeImageTemplate")
	if anonymizeImageTemplate != "" {
		anonymizeImageAPIRequest.AnonymizeImageTemplate = &types.AnonymizeImageTemplate{}
		presidio.ConvertJSONToInterface(anonymizeImageTemplate, &anonymizeImageAPIRequest.AnonymizeImageTemplate)
	}

	anonymizeImageAPIRequest.AnonymizeImageTemplateId, _ = c.GetPostForm("anonymizeImageTemplateId")

	analyzeTemplate, _ := c.GetPostForm("analyzeTemplate")
	if analyzeTemplate != "" {
		anonymizeImageAPIRequest.AnalyzeTemplate = &types.AnalyzeTemplate{}
		presidio.ConvertJSONToInterface(analyzeTemplate, &anonymizeImageAPIRequest.AnalyzeTemplate)
	}

	anonymizeImageAPIRequest.AnalyzeTemplateId, _ = c.GetPostForm("analyzeTemplateId")

	file, err := c.FormFile("file")
	if err != nil {
		return nil, err
	}
	anonymizeImageAPIRequest.Data, err = openFile(file)
	if err != nil {
		return nil, err
	}
	return anonymizeImageAPIRequest, nil
}

func scheduleScannerCronJob(c *gin.Context) {
	var scannerCronJobAPIRequest *types.ScannerCronJobApiRequest
	project := c.Param("project")
	if c.Bind(&scannerCronJobAPIRequest) == nil {
		result, err := scj.ScheduleScannerCronJob(c, api, scannerCronJobAPIRequest, project)
		if err != nil {
			server.AbortWithError(c, http.StatusBadRequest, err)
			return
		}
		server.WriteResponse(c, http.StatusOK, result)
	}
}

func scheduleStreamJob(c *gin.Context) {
	var streamsJobAPIRequest *types.StreamsJobApiRequest
	project := c.Param("project")
	if c.Bind(&streamsJobAPIRequest) == nil {
		result, err := sj.ScheduleStreamsJob(c, api, streamsJobAPIRequest, project)
		if err != nil {
			server.AbortWithError(c, http.StatusBadRequest, err)
			return
		}
		server.WriteResponse(c, http.StatusOK, result)
	}
}

func validateTemplate(action string, c *gin.Context) (string, error) {
	switch action {
	case store.Analyze:
		var analyzerTemplate types.AnalyzeTemplate
		return bindAndConvert(analyzerTemplate, c)
	case store.Anonymize:
		var anonymizeTemplate types.AnonymizeTemplate
		return bindAndConvert(anonymizeTemplate, c)
	case store.AnonymizeImage:
		var anonymizeImageTemplate types.AnonymizeImageTemplate
		return bindAndConvert(anonymizeImageTemplate, c)
	case store.Scan:
		var scanTemplate types.ScanTemplate
		return bindAndConvert(scanTemplate, c)
	case store.Datasink:
		var datasinkTemplate types.DatasinkTemplate
		return bindAndConvert(datasinkTemplate, c)
	case store.ScheduleScannerCronJob:
		var scannerCronjobTemplate types.ScannerCronJobTemplate
		return bindAndConvert(scannerCronjobTemplate, c)
	case store.ScheduleStreamsJob:
		var streamsJobTemplate types.StreamsJobTemplate
		return bindAndConvert(streamsJobTemplate, c)
	case store.Stream:
		var streamTemplate types.StreamTemplate
		return bindAndConvert(streamTemplate, c)
	}

	return "", fmt.Errorf("No template found")
}

func bindAndConvert(template interface{}, c *gin.Context) (string, error) {
	if c.BindJSON(&template) == nil {
		return presidio.ConvertInterfaceToJSON(template)
	}
	return "", fmt.Errorf("No template found")
}

func openFile(header *multipart.FileHeader) ([]byte, error) {

	file, err := header.Open()
	if err != nil {
		return nil, err
	}

	defer file.Close()
	bt := make([]byte, header.Size)
	_, err = file.Read(bt)
	if err != nil {
		return nil, err
	}

	return bt, nil
}

func insertRecognizer(c *gin.Context) {
	var request *types.RecognizerInsertOrUpdateRequest
	id := c.Param("id")
	if c.Bind(&request) == nil {
		request.Value.Name = id
		result, err := recognizers.InsertRecognizer(
			c, api, request)
		if err != nil {
			server.AbortWithError(c, http.StatusBadRequest, err)
			return
		}
		server.WriteResponse(c, http.StatusOK, result)
	}
}

func updateRecognizer(c *gin.Context) {
	var request *types.RecognizerInsertOrUpdateRequest
	id := c.Param("id")
	if c.Bind(&request) == nil {
		request.Value.Name = id
		result, err := recognizers.UpdateRecognizer(
			c, api, request)
		if err != nil {
			server.AbortWithError(c, http.StatusBadRequest, err)
			return
		}
		server.WriteResponse(c, http.StatusOK, result)
	}
}

func deleteRecognizer(c *gin.Context) {
	var request types.RecognizerDeleteRequest
	id := c.Param("id")
	request.Name = id
	result, err := recognizers.DeleteRecognizer(
		c, api, &request)
	if err != nil {
		server.AbortWithError(c, http.StatusBadRequest, err)
		return
	}
	server.WriteResponse(c, http.StatusOK, result)
}

func getRecognizer(c *gin.Context) {
	var request types.RecognizerGetRequest
	id := c.Param("id")
	request.Name = id
	result, err := recognizers.GetRecognizer(
		c, api, &request)
	if err != nil {
		server.AbortWithError(c, http.StatusBadRequest, err)
		return
	}
	server.WriteResponse(c, http.StatusOK, result)
}

func getAllRecognizers(c *gin.Context) {
	var request *types.RecognizersGetAllRequest
	result, err := recognizers.GetAllRecognizers(
		c, api, request)
	if err != nil {
		server.AbortWithError(c, http.StatusBadRequest, err)
		return
	}
	server.WriteResponse(c, http.StatusOK, result)
}
