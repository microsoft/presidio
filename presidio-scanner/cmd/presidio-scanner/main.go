package main

import (
	"context"
	"fmt"
	"os"

	"github.com/Microsoft/presidio/presidio-scanner/cmd/presidio-scanner/item"

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
	dataSyncService := setupDataSyncService(scanRequest.DataSyncTemplate)
	scanner := createScanner(scanRequest)

	// Scan
	_, err := Scan(scanner, scanRequest, cache, analyzeService, analyzeRequest, anonymizeService, dataSyncService)

	if err != nil {
		log.Fatal(err.Error())
	}

	// notify dataSync that scanner is done
	(*dataSyncService).Completion(context.Background(), &message_types.CompletionMessage{})
	log.Info("Done!")
}

//Scan the data
func Scan(scanner scanner.Scanner, scanRequest *message_types.ScanRequest, cache cache.Cache,
	analyzeService *message_types.AnalyzeServiceClient, analyzeRequest *message_types.AnalyzeRequest,
	anonymizeService *message_types.AnonymizeServiceClient, dataSyncService *message_types.DataSyncServiceClient) (int, error) {

	return scanner.Scan(func(item interface{}) (int, error) {
		var analyzerResult []*message_types.AnalyzeResult
		var text string

		scanItem := createItem(scanRequest.Kind, item)
		itemPath := scanItem.GetPath()
		uniqueID, err := scanItem.GetUniqueID()
		if err != nil {
			log.Error(fmt.Sprintf("error getting item id: %s, error: %q", itemPath, err.Error()))
			return 0, err
		}

		shouldScan, err := shouldScanItem(&cache, scanItem, uniqueID)
		if err != nil {
			log.Error(fmt.Sprintf("error getting item from cache: %s, error: %q", itemPath, err.Error()))
			return 0, err
		}

		if shouldScan {
			text, analyzerResult, err = analyzeItem(analyzeService, analyzeRequest, scanItem)
			if err != nil {
				log.Error(fmt.Sprintf("error scanning file: %s, error: %q", itemPath, err.Error()))
				return 0, err
			}

			if len(analyzerResult) > 0 {
				anonymizerResult, err := anonymizeItem(analyzerResult, text, itemPath, scanRequest.AnonymizeTemplate, anonymizeService)

				if err != nil {
					log.Error(fmt.Sprintf("error anonymizing item: %s, error: %q", itemPath, err.Error()))
					return 0, err
				}

				err = sendResultToDataSync(itemPath, analyzerResult, anonymizerResult, cache, dataSyncService)
				if err != nil {
					log.Error(fmt.Sprintf("error sending file to dataSync: %s, error: %q", itemPath, err.Error()))
					return 0, err
				}
				log.Info(fmt.Sprintf("%d results were sent to the dataSync successfully", len(analyzerResult)))

			}
			writeItemToCache(uniqueID, itemPath, cache)
			return 1, nil
		}

		log.Info(fmt.Sprintf("item %s was already scanned", itemPath))
		return 0, nil
	})
}

func anonymizeItem(analyzeResults []*message_types.AnalyzeResult, text string, path string, anonymizeTemplate *message_types.AnonymizeTemplate,
	anonymizeService *message_types.AnonymizeServiceClient) (*message_types.AnonymizeResponse, error) {
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

func writeItemToCache(uniqueID string, scannedPath string, cache cache.Cache) {
	// If writing to dataSync succeeded - update the cache
	err := cache.Set(uniqueID, scannedPath)
	if err != nil {
		log.Error(err.Error())
	}
}

func sendResultToDataSync(scannedPath string, analyzeResults []*message_types.AnalyzeResult,
	anonymizeResults *message_types.AnonymizeResponse, cache cache.Cache,
	dataSyncService *message_types.DataSyncServiceClient) error {
	srv := *dataSyncService

	for _, element := range analyzeResults {
		// Remove PII from results
		element.Text = ""
	}

	dataSyncRequest := &message_types.DataSyncRequest{
		AnalyzeResults:  analyzeResults,
		AnonymizeResult: anonymizeResults,
		Path:            scannedPath,
	}

	_, err := srv.Apply(context.Background(), dataSyncRequest)
	return err
}

func setupDataSyncService(dataSyncTemplate *message_types.DataSyncTemplate) *message_types.DataSyncServiceClient {
	dataSyncService, err := rpc.SetupDataSyncService(fmt.Sprintf("localhost:%s", grpcPort))
	if err != nil {
		log.Fatal(fmt.Sprintf("Connection to dataSync service failed %q", err))
	}

	_, err = (*dataSyncService).Init(context.Background(), dataSyncTemplate)
	if err != nil {
		log.Fatal(err.Error())
	}

	return dataSyncService
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
		log.Fatal(fmt.Sprintf("Connection to analyzer service failed %q", err))
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
		log.Fatal(fmt.Sprintf("Connection to anonymizer service failed %q", err))
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
		log.Fatal(fmt.Sprintf("Error formating scanner request %q", err.Error()))
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

func shouldScanItem(cache *cache.Cache, item item.Item, uniqueID string) (bool, error) {
	err := item.IsContentTypeSupported()
	if err != nil {
		return false, err
	}

	val, err := (*cache).Get(uniqueID)
	if err != nil {
		return false, err
	}

	// if value is not in cache, cache.get will return ""
	shouldScan := val == ""
	return shouldScan, nil
}

// Sends analyzer scan request to the analyzer service and returns analyzer result
func analyzeItem(
	analyzeService *message_types.AnalyzeServiceClient,
	analyzeRequest *message_types.AnalyzeRequest,
	item item.Item) (string, []*message_types.AnalyzeResult, error) {

	// Value not found in the cache. Need to scan the file and update the cache
	itemContent, err := item.GetContent()
	if err != nil {
		return "", nil, fmt.Errorf("error getting item's content, error: %q", err.Error())
	}

	analyzeRequest.Text = itemContent

	srv := *analyzeService
	results, err := srv.Apply(context.Background(), analyzeRequest)
	if err != nil {
		return "", nil, err
	}

	return itemContent, results.AnalyzeResults, nil
}
