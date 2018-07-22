package main

import (
	"fmt"
	"net/http"
	"os"

	"github.com/gin-gonic/gin"

	log "github.com/presid-io/presidio/pkg/logger"
	analyzer "github.com/presid-io/presidio/pkg/modules/analyzer"
	"github.com/presid-io/presidio/pkg/rpc"

	message_types "github.com/presid-io/presidio-genproto/golang"
	helper "github.com/presid-io/presidio/pkg/helper"
	server "github.com/presid-io/presidio/pkg/server"
	templates "github.com/presid-io/presidio/pkg/templates"
)

var analyzeService *message_types.AnalyzeServiceClient
var anonymizeService *message_types.AnonymizeServiceClient

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

func (api *API) invokeAnonymize(project string, id string, text string, results []*message_types.AnalyzeResult, c *gin.Context) *message_types.AnonymizeResponse {
	anonymizeKey := templates.CreateKey(project, "anonymize", id)
	result, err := api.templates.GetTemplate(anonymizeKey)

	if err != nil {
		c.AbortWithError(http.StatusBadRequest, err)
		return nil
	}
	srv := *anonymizeService
	anonymizeTemplate := &message_types.AnonymizeTemplate{}
	err = helper.ConvertJSONToInterface(result, anonymizeTemplate)
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
	analyzeRequest, err := analyzer.GetAnalyzeRequest(api.templates, analyzeKey)

	if err != nil {
		c.AbortWithError(http.StatusBadRequest, err)
		return nil
	}

	analyzerObj := analyzer.New(analyzeService)
	analyzeRequest.Text = text
	analyzeResponse, err := analyzerObj.InvokeAnalyze(c, analyzeRequest)
	if err != nil {
		c.AbortWithError(http.StatusInternalServerError, err)
		return nil
	}
	return analyzeResponse
}
