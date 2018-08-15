package main

import (
	"context"
	"os"

	message_types "github.com/Microsoft/presidio-genproto/golang"
	log "github.com/Microsoft/presidio/pkg/logger"
	services "github.com/Microsoft/presidio/pkg/presidio"
	"github.com/Microsoft/presidio/pkg/templates"
	"github.com/Microsoft/presidio/presidio-scanner/cmd/presidio-scanner/scanner"
)

var (
	grpcPort string
)

func main() {
	// Setup objects
	scanRequest := initScanner()
	cache := services.SetupCache()
	analyzeRequest, analyzeService := setupAnalyzerObjects(scanRequest)
	anonymizeService := setupAnoymizerService(scanRequest)
	datasinkService := setupDatasinkService(scanRequest.DatasinkTemplate)
	s := scanner.CreateScanner(scanRequest)

	// Scan
	_, err := scanner.ScanData(s, scanRequest, cache, analyzeService, analyzeRequest, anonymizeService, datasinkService)

	if err != nil {
		log.Fatal(err.Error())
	}

	// notify datasink that scanner is done
	(*datasinkService).Completion(context.Background(), &message_types.CompletionMessage{})
	log.Info("Done!")
}

// Init functions
func setupAnalyzerObjects(scanRequest *message_types.ScanRequest) (*message_types.AnalyzeRequest, *message_types.AnalyzeServiceClient) {
	analyzeService := services.SetupAnalyzerService()

	analyzeRequest := &message_types.AnalyzeRequest{
		AnalyzeTemplate: scanRequest.GetAnalyzeTemplate(),
	}

	return analyzeRequest, analyzeService
}

func setupAnoymizerService(scanRequest *message_types.ScanRequest) *message_types.AnonymizeServiceClient {
	// Anonymize is not mandatory - initialize objects only if needed
	if scanRequest.AnonymizeTemplate == nil {
		return nil
	}

	return services.SetupAnoymizerService()
}

func initScanner() *message_types.ScanRequest {
	scannerObj := os.Getenv("SCANNER_REQUEST")
	scanRequest := &message_types.ScanRequest{}
	err := templates.ConvertJSONToInterface(scannerObj, scanRequest)
	if err != nil {
		log.Fatal("Error formating scanner request %q", err.Error())
	}

	grpcPort = os.Getenv("GRPC_PORT")
	if grpcPort == "" {
		// Set to default
		grpcPort = "5000"
	}

	return scanRequest
}

func setupDatasinkService(datasinkTemplate *message_types.DatasinkTemplate) *message_types.DatasinkServiceClient {
	datasinkService := services.SetupDatasinkService()

	_, err := (*datasinkService).Init(context.Background(), datasinkTemplate)
	if err != nil {
		log.Fatal(err.Error())
	}

	return datasinkService
}
