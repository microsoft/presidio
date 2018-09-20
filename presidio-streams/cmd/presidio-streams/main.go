package main

import (
	"context"
	"fmt"

	types "github.com/Microsoft/presidio-genproto/golang"
	log "github.com/Microsoft/presidio/pkg/logger"
	"github.com/Microsoft/presidio/pkg/platform"
	services "github.com/Microsoft/presidio/pkg/presidio"
	"github.com/Microsoft/presidio/pkg/templates"
)

var analyzeService *types.AnalyzeServiceClient
var anonymizeService *types.AnonymizeServiceClient
var datasinkService *types.DatasinkServiceClient
var streamRequest *types.StreamRequest

func main() {
	initStream()

	analyzeService = services.SetupAnalyzerService()

	if streamRequest.AnonymizeTemplate != nil {
		anonymizeService = services.SetupAnonymizerService()
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

func sendResultToDatasink(analyzeResults []*types.AnalyzeResult,
	anonymizeResults *types.AnonymizeResponse, path string) error {
	srv := *datasinkService

	for _, element := range analyzeResults {
		// Remove PII from results
		element.Text = ""
	}

	datasinkRequest := &types.DatasinkRequest{
		AnalyzeResults:  analyzeResults,
		AnonymizeResult: anonymizeResults,
		Path:            path,
	}

	_, err := srv.Apply(context.Background(), datasinkRequest)
	return err
}

func initStream() {

	settings := platform.GetSettings()
	streamRequest = &types.StreamRequest{}

	err := templates.ConvertJSONToInterface(settings.StreamRequest, streamRequest)
	if err != nil {
		log.Fatal("Error formating scanner request %q", err.Error())
	}
}

func setupDatasinkService(datasinkTemplate *types.DatasinkTemplate) {
	datasinkService = services.SetupDatasinkService()

	_, err := (*datasinkService).Init(context.Background(), datasinkTemplate)
	if err != nil {
		log.Fatal(err.Error())
	}
}

func analyzeItem(text string) ([]*types.AnalyzeResult, error) {
	analyzeRequest := &types.AnalyzeRequest{
		AnalyzeTemplate: streamRequest.GetAnalyzeTemplate(),
		Text:            text,
	}

	srv := *analyzeService
	results, err := srv.Apply(context.Background(), analyzeRequest)
	if err != nil {
		return nil, err
	}

	return results.AnalyzeResults, nil
}

func anonymizeItem(analyzeResults []*types.AnalyzeResult, text string, anonymizeTemplate *types.AnonymizeTemplate) (*types.AnonymizeResponse, error) {
	if anonymizeTemplate != nil {
		srv := *anonymizeService

		anonymizeRequest := &types.AnonymizeRequest{
			Template:       anonymizeTemplate,
			Text:           text,
			AnalyzeResults: analyzeResults,
		}
		res, err := srv.Apply(context.Background(), anonymizeRequest)
		return res, err
	}
	return nil, nil
}
