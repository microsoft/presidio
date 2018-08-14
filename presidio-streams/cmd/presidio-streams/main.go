package main

import (
	"context"
	"fmt"
	"os"

	message_types "github.com/Microsoft/presidio-genproto/golang"
	log "github.com/Microsoft/presidio/pkg/logger"
	services "github.com/Microsoft/presidio/pkg/presidio"
	"github.com/Microsoft/presidio/pkg/templates"
)

var analyzeService *message_types.AnalyzeServiceClient
var anonymizeService *message_types.AnonymizeServiceClient
var datasinkService *message_types.DatasinkServiceClient
var streamRequest *message_types.StreamRequest

func main() {
	initStream()

	analyzeService = services.SetupAnalyzerService()

	if streamRequest.AnonymizeTemplate != nil {
		anonymizeService = services.SetupAnoymizerService()
	}

	setupDatasinkService(streamRequest.DatasinkTemplate)

	stream := createStream()
	err := stream.Receive(receiveEvents)

	if err != nil {
		log.Error(err.Error())
	}
}

func receiveEvents(partition string, sequence string, text string) error {
	analyzerResult, err := analyzeItem(text)
	if err != nil {
		log.Error("error analyzing message: %s, error: %q", text, err.Error())
		return err
	}

	if len(analyzerResult) > 0 {
		anonymizerResult, err := anonymizeItem(analyzerResult, text, streamRequest.AnonymizeTemplate)

		if err != nil {
			log.Error("error anonymizing item: %s/%s, error: %q", partition, sequence, err.Error())
			return err
		}

		err = sendResultToDatasink(analyzerResult, anonymizerResult, fmt.Sprintf("%s/%s", partition, sequence))
		if err != nil {
			log.Error("error sending message to datasink: %s/%s, error: %q", partition, sequence, err.Error())
			return err
		}
		log.Info("%d results were sent to the datasink successfully", len(analyzerResult))

	}
	return nil
}

func sendResultToDatasink(analyzeResults []*message_types.AnalyzeResult,
	anonymizeResults *message_types.AnonymizeResponse, path string) error {
	srv := *datasinkService

	for _, element := range analyzeResults {
		// Remove PII from results
		element.Text = ""
	}

	datasinkRequest := &message_types.DatasinkRequest{
		AnalyzeResults:  analyzeResults,
		AnonymizeResult: anonymizeResults,
		Path:            path,
	}

	_, err := srv.Apply(context.Background(), datasinkRequest)
	return err
}

func initStream() {

	streamObj := os.Getenv("STREAM_REQUEST")
	streamRequest = &message_types.StreamRequest{}
	err := templates.ConvertJSONToInterface(streamObj, streamRequest)
	if err != nil {
		log.Fatal("Error formating scanner request %q", err.Error())
	}

	if streamRequest.Kind == "" {
		log.Fatal("stream kind var must me set")
	}

}

func setupDatasinkService(datasinkTemplate *message_types.DatasinkTemplate) {
	datasinkService = services.SetupDatasinkService()

	_, err := (*datasinkService).Init(context.Background(), datasinkTemplate)
	if err != nil {
		log.Fatal(err.Error())
	}
}

func analyzeItem(text string) ([]*message_types.AnalyzeResult, error) {

	analyzeRequest := &message_types.AnalyzeRequest{
		AnalyzeTemplate: streamRequest.GetAnalyzeTemplate(),
		MinProbability:  streamRequest.GetMinProbability(),
		Text:            text,
	}

	srv := *analyzeService
	results, err := srv.Apply(context.Background(), analyzeRequest)
	if err != nil {
		return nil, err
	}

	return results.AnalyzeResults, nil
}

func anonymizeItem(analyzeResults []*message_types.AnalyzeResult, text string, anonymizeTemplate *message_types.AnonymizeTemplate) (*message_types.AnonymizeResponse, error) {
	if anonymizeTemplate != nil {
		srv := *anonymizeService

		anonymizeRequest := &message_types.AnonymizeRequest{
			Template:       anonymizeTemplate,
			Text:           text,
			AnalyzeResults: analyzeResults,
		}
		res, err := srv.Apply(context.Background(), anonymizeRequest)
		return res, err
	}
	return nil, nil
}
