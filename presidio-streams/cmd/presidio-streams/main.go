package main

import (
	"context"
	"fmt"
	"os"

	"github.com/joho/godotenv"

	message_types "github.com/Microsoft/presidio-genproto/golang"
	log "github.com/Microsoft/presidio/pkg/logger"
	"github.com/Microsoft/presidio/pkg/rpc"
	"github.com/Microsoft/presidio/pkg/templates"
)

var (
	streamKind         string
	dataBinderGRPCPort string
	analyzeRequest     *message_types.AnalyzeRequest
	analyzeService     *message_types.AnalyzeServiceClient
	streamRequest      *message_types.StreamRequest
)

func main() {
	setupAnalyzerObjects()
	initStream()
	setupDataBinderService()
	stream := createStream()
	err := stream.Receive(receiveEvents)

	if err != nil {
		log.Error(err.Error())
	}
}

func receiveEvents(data string) {

}

func initStream() {
	godotenv.Load()

	streamObj := os.Getenv("STREAM_REQUEST")
	template := &message_types.StreamRequest{}
	err := templates.ConvertJSONToInterface(streamObj, template)
	if err != nil {
		log.Fatal(fmt.Sprintf("Error formating scanner template %q", err.Error()))
	}
	streamRequest = template
	streamKind = streamRequest.Kind

	if streamKind == "" {
		log.Fatal("stream kind var must me set")
	}

	// TODO: Change!!
	dataBinderGRPCPort = os.Getenv("DATABINDER_GRPC_PORT")
	if dataBinderGRPCPort == "" {
		// Set to default
		dataBinderGRPCPort = "5000"
	}
}

func setupDataBinderService() *message_types.DatabinderServiceClient {
	databinderService, err := rpc.SetupDataBinderService(fmt.Sprintf("localhost:%s", dataBinderGRPCPort))
	if err != nil {
		log.Fatal(fmt.Sprintf("Connection to databinder service failed %q", err))
	}

	_, err = (*databinderService).Init(context.Background(), streamRequest.DatabinderTemplate)
	if err != nil {
		log.Fatal(err.Error())
	}

	return databinderService
}

func setupAnalyzerObjects() {
	analyzerSvcHost := os.Getenv("ANALYZER_SVC_HOST")
	if analyzerSvcHost == "" {
		log.Fatal("analyzer service address is empty")
	}

	analyzerSvcPort := os.Getenv("ANALYZER_SVC_PORT")
	if analyzerSvcPort == "" {
		log.Fatal("analyzer service port is empty")
	}

	var err error
	analyzeService, err = rpc.SetupAnalyzerService(analyzerSvcHost + ":" + analyzerSvcPort)
	if err != nil {
		log.Error(fmt.Sprintf("Connection to analyzer service failed %q", err))
	}

	analyzeRequest = &message_types.AnalyzeRequest{
		AnalyzeTemplate: streamRequest.GetAnalyzeTemplate(),
		MinProbability:  streamRequest.GetMinProbability(),
	}

	if err != nil {
		log.Fatal(err.Error())
	}
}
