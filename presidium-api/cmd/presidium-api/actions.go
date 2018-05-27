package main

import (
	"fmt"
	"net/http"

	"github.com/gin-gonic/gin"

	"github.com/presidium-io/presidium/pkg/service-discovery/consul"

	log "github.com/presidium-io/presidium/pkg/logger"
	"github.com/presidium-io/presidium/pkg/rpc"

	server "github.com/presidium-io/presidium/pkg/server"
	message_types "github.com/presidium-io/presidium/pkg/types"
)

var analyzeService *message_types.AnalyzeServiceClient
var anonymizeService *message_types.AnonymizeServiceClient

func setupGrpcServices() {
	store := consul.New()
	var err error
	var analyzerSvcHost, anonymizerSvcHost string

	analyzerSvcHost, err = store.GetService("analyzer")
	if err != nil {
		log.Fatal(fmt.Sprintf("analyzer service address is empty %q", err))
	}

	anonymizerSvcHost, err = store.GetService("anonymizer")
	if err != nil {
		log.Fatal(fmt.Sprintf("anonymizer service address is empty %q", err))
	}

	analyzeService, err = rpc.SetupAnalyzerService(analyzerSvcHost)
	if err != nil {
		log.Error(fmt.Sprintf("Connection to analyzer service failed %q", err))
	}
	anonymizeService, err = rpc.SetupAnonymizeService(anonymizerSvcHost)
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

		anonymizeRes := api.invokeAnonymize(project, id, anonymizeAPIRequest.Text, analyzeRes.Results, c)
		if anonymizeRes == nil {
			return
		}
		server.WriteResponse(c, http.StatusOK, anonymizeRes)
	}
}

func (api *API) invokeAnonymize(project string, id string, text string, results []*message_types.Result, c *gin.Context) *message_types.AnonymizeResponse {
	result, err := api.getTemplate(project, "anonymize", id)

	if err != nil {
		server.WriteResponse(c, http.StatusBadRequest, fmt.Sprintf("Failed to retrieve template %q", err))
		return nil
	}
	srv := *anonymizeService
	anonymizeTemplate := &message_types.AnonymizeTemplate{}
	err = convertJSON2Interface(result, anonymizeTemplate)
	if err != nil {
		server.WriteResponse(c, http.StatusBadRequest, fmt.Sprintf("Failed to convert template %q", err))
		return nil
	}
	request := &message_types.AnonymizeRequest{
		Template: anonymizeTemplate,
		Text:     text,
		Results:  results,
	}
	res, err := srv.Apply(c, request)
	if err != nil {
		server.WriteResponse(c, http.StatusBadRequest, err.Error())
		return nil
	}
	return res
}
func (api *API) invokeAnalyze(project string, id string, text string, c *gin.Context) *message_types.Results {
	result, err := api.getTemplate(project, "analyze", id)

	if err != nil {
		server.WriteResponse(c, http.StatusBadRequest, fmt.Sprintf("Failed to retrieve template %q", err))
		return nil
	}
	srv := *analyzeService
	analyzeRequest := &message_types.AnalyzeRequest{}
	err = convertJSON2Interface(result, analyzeRequest)
	if err != nil {
		server.WriteResponse(c, http.StatusBadRequest, fmt.Sprintf("Failed to convert template %q", err))
		return nil
	}
	analyzeRequest.Value = text
	res, err := srv.Apply(c, analyzeRequest)
	if err != nil {
		server.WriteResponse(c, http.StatusBadRequest, err.Error())
		return nil
	}
	return res
}
