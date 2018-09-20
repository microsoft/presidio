package main

import (
	"context"

	types "github.com/Microsoft/presidio-genproto/golang"
	log "github.com/Microsoft/presidio/pkg/logger"
	"github.com/Microsoft/presidio/pkg/platform"
	services "github.com/Microsoft/presidio/pkg/presidio"
	"github.com/Microsoft/presidio/pkg/templates"
	"github.com/Microsoft/presidio/presidio-scanner/cmd/presidio-scanner/scanner"
)

func main() {
	// Setup objects
	scanRequest := initScanner()
	cache := services.SetupCache()
	analyzeRequest, analyzeService := setupAnalyzerObjects(scanRequest)
	anonymizeService := setupAnonymizerService(scanRequest)
	datasinkService := setupDatasinkService(scanRequest.DatasinkTemplate)
	s := scanner.CreateScanner(scanRequest)

	// Scan
	err := scanner.ScanData(s, scanRequest, cache, analyzeService, analyzeRequest, anonymizeService, datasinkService)

	if err != nil {
		log.Fatal(err.Error())
	}

	// notify datasink that scanner is done
	(*datasinkService).Completion(context.Background(), &types.CompletionMessage{})
	log.Info("Done!")
}

// Init functions
func setupAnalyzerObjects(scanRequest *types.ScanRequest) (*types.AnalyzeRequest, *types.AnalyzeServiceClient) {
	analyzeService := services.SetupAnalyzerService()

	analyzeRequest := &types.AnalyzeRequest{
		AnalyzeTemplate: scanRequest.GetAnalyzeTemplate(),
	}

	return analyzeRequest, analyzeService
}

func setupAnonymizerService(scanRequest *types.ScanRequest) *types.AnonymizeServiceClient {
	// Anonymize is not mandatory - initialize objects only if needed
	if scanRequest.AnonymizeTemplate == nil {
		return nil
	}

	return services.SetupAnonymizerService()
}

func initScanner() *types.ScanRequest {

	settings := platform.GetSettings()

	scanRequest := &types.ScanRequest{}
	err := templates.ConvertJSONToInterface(settings.ScannerRequest, scanRequest)
	if err != nil {
		log.Fatal("Error formating scanner request %q", err.Error())
	}

	if settings.GrpcPort == "" {
		// Set to default
		settings.GrpcPort = "5000"
	}

	return scanRequest
}

func setupDatasinkService(datasinkTemplate *types.DatasinkTemplate) *types.DatasinkServiceClient {
	datasinkService := services.SetupDatasinkService()

	_, err := (*datasinkService).Init(context.Background(), datasinkTemplate)
	if err != nil {
		log.Fatal(err.Error())
	}

	return datasinkService
}
