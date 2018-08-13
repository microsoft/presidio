package main

import (
	"context"
	"fmt"
	"os"

	"github.com/joho/godotenv"

	message_types "github.com/Microsoft/presidio-genproto/golang"
	"github.com/Microsoft/presidio/pkg/cache"
	"github.com/Microsoft/presidio/pkg/cache/redis"
	log "github.com/Microsoft/presidio/pkg/logger"
	"github.com/Microsoft/presidio/pkg/rpc"
	"github.com/Microsoft/presidio/pkg/templates"
	"github.com/Microsoft/presidio/presidio-scanner/cmd/presidio-scanner/scanner"
)

var (
	grpcPort string
)

func main() {
	// Setup objects
	scanRequest := initScanner()
	cache := setupCache()
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
	analyzerSvcHost := os.Getenv("ANALYZER_SVC_HOST")
	if analyzerSvcHost == "" {
		log.Fatal("analyzer service address is empty")
	}

	analyzerSvcPort := os.Getenv("ANALYZER_SVC_PORT")
	if analyzerSvcPort == "" {
		log.Fatal("analyzer service port is empty")
	}

	analyzeService, err := rpc.SetupAnalyzerService(analyzerSvcHost + ":" + analyzerSvcPort)
	if err != nil {
		log.Fatal("Connection to analyzer service failed %q", err)
	}

	analyzeRequest := &message_types.AnalyzeRequest{
		AnalyzeTemplate: scanRequest.GetAnalyzeTemplate(),
		MinProbability:  scanRequest.GetMinProbability(),
	}

	return analyzeRequest, analyzeService
}

func setupAnoymizerService(scanRequest *message_types.ScanRequest) *message_types.AnonymizeServiceClient {
	// Anonymize is not mandatory - initialize objects only if needed
	if scanRequest.AnonymizeTemplate == nil {
		return nil
	}

	anonymizerSvcHost := os.Getenv("ANONYMIZER_SVC_HOST")
	if anonymizerSvcHost == "" {
		log.Fatal("anonymizer service address is empty")
	}

	anonymizerSvcPort := os.Getenv("ANONYMIZER_SVC_PORT")
	if anonymizerSvcPort == "" {
		log.Fatal("anonymizer service port is empty")
	}

	anonymizeService, err := rpc.SetupAnonymizeService(anonymizerSvcHost + ":" + anonymizerSvcPort)
	if err != nil {
		log.Fatal("Connection to anonymizer service failed %q", err)
	}
	return anonymizeService
}

func setupCache() cache.Cache {
	redisHost := os.Getenv("REDIS_HOST")
	if redisHost == "" {
		log.Fatal("redis address is empty")
	}

	redisPort := os.Getenv("REDIS_SVC_PORT")
	if redisPort == "" {
		log.Fatal("redis port is empty")
	}

	redisAddress := redisHost + ":" + redisPort
	cache := redis.New(
		redisAddress,
		"", // no password set
		0,  // use default DB
	)
	return cache
}

func initScanner() *message_types.ScanRequest {
	godotenv.Load()

	scannerObj := os.Getenv("SCANNER_REQUEST")
	scanRequest := &message_types.ScanRequest{}
	err := templates.ConvertJSONToInterface(scannerObj, scanRequest)
	if err != nil {
		log.Fatal("Error formating scanner request %q", err.Error())
	}

	if scanRequest.Kind == "" {
		log.Fatal("storage king var must me set")
	}

	grpcPort = os.Getenv("GRPC_PORT")
	if grpcPort == "" {
		// Set to default
		grpcPort = "5000"
	}

	return scanRequest
}

func setupDatasinkService(datasinkTemplate *message_types.DatasinkTemplate) *message_types.DatasinkServiceClient {
	datasinkService, err := rpc.SetupDatasinkService(fmt.Sprintf("localhost:%s", grpcPort))
	if err != nil {
		log.Fatal("Connection to datasink service failed %q", err)
	}

	_, err = (*datasinkService).Init(context.Background(), datasinkTemplate)
	if err != nil {
		log.Fatal(err.Error())
	}

	return datasinkService
}
