package main

import (
	"context"
	"fmt"
	"os"

	"github.com/joho/godotenv"

	message_types "github.com/presid-io/presidio-genproto/golang"
	"github.com/presid-io/presidio/pkg/cache"
	"github.com/presid-io/presidio/pkg/cache/redis"
	log "github.com/presid-io/presidio/pkg/logger"
	"github.com/presid-io/presidio/pkg/rpc"
	"github.com/presid-io/presidio/pkg/templates"
	"github.com/presid-io/presidio/presidio-scanner/cmd/presidio-scanner/scanner"
)

var (
	storageKind      string
	grpcPort         string
	analyzeRequest   *message_types.AnalyzeRequest
	analyzeService   *message_types.AnalyzeServiceClient
	anonymizeService *message_types.AnonymizeServiceClient
	scannerObj       scanner.Scanner
	scanRequest      *message_types.ScanRequest
)

func main() {
	// Setup objects
	initScanner()

	cache := setupCache()
	setupAnalyzerObjects()
	setupAnoymizerService()
	databinderService := setupDataBinderService()
	scannerObj = createScanner(scanRequest)

	err := scannerObj.WalkItems(func(item interface{}) {
		var analyzerResult []*message_types.AnalyzeResult
		var text string

		itemPath := scannerObj.GetItemPath(item)
		uniqueID, err := scannerObj.GetItemUniqueID(item)
		if err != nil {
			log.Error(fmt.Sprintf("error getting item path: %s, error: %q", itemPath, err.Error()))
			return
		}

		text, analyzerResult, err = analyzeItem(&cache, uniqueID, analyzeService, analyzeRequest, item)
		if err != nil {
			log.Error(fmt.Sprintf("error scanning file: %s, error: %q", itemPath, err.Error()))
			return
		}

		if text == "" {
			log.Info(fmt.Sprintf("item %s was already scanned", itemPath))
		}

		if len(analyzerResult) > 0 {
			anonymizerResult, err := anonymizeItem(analyzerResult, text, itemPath)

			if err != nil {
				log.Error(fmt.Sprintf("error anonymizing item: %s, error: %q", itemPath, err.Error()))
				return
			}

			err = sendResultToDataBinder(itemPath, analyzerResult, anonymizerResult, cache, databinderService)
			if err != nil {
				log.Error(fmt.Sprintf("error sending file to databinder: %s, error: %q", itemPath, err.Error()))
				return
			}
			log.Info(fmt.Sprintf("%d results were sent to the databinder successfully", len(analyzerResult)))

		}

		writeItemToCache(uniqueID, itemPath, cache)
	})

	if err != nil {
		log.Fatal(err.Error())
	}

	log.Info("Done!")
}

func anonymizeItem(analyzeResults []*message_types.AnalyzeResult, text string, path string) (*message_types.AnonymizeResponse, error) {
	if scanRequest.AnonymizeTemplate != nil {
		srv := *anonymizeService

		anonymizeRequest := &message_types.AnonymizeRequest{
			Template:       scanRequest.AnonymizeTemplate,
			Text:           text,
			AnalyzeResults: analyzeResults,
		}
		res, err := srv.Apply(context.Background(), anonymizeRequest)
		return res, err
	}
	return nil, nil
}

func writeItemToCache(uniqueID string, scannedPath string, cache cache.Cache) {
	// If writing to databinder succeeded - update the cache
	err := cache.Set(uniqueID, scannedPath)
	if err != nil {
		log.Error(err.Error())
	}
}

func sendResultToDataBinder(scannedPath string, analyzeResults []*message_types.AnalyzeResult,
	anonymizeResults *message_types.AnonymizeResponse, cache cache.Cache,
	databinderService *message_types.DatabinderServiceClient) error {
	srv := *databinderService

	for _, element := range analyzeResults {
		// Remove PII from results
		element.Text = ""
	}

	databinderRequest := &message_types.DatabinderRequest{
		AnalyzeResults:  analyzeResults,
		AnonymizeResult: anonymizeResults,
		Path:            scannedPath,
	}

	_, err := srv.Apply(context.Background(), databinderRequest)
	return err
}

func setupDataBinderService() *message_types.DatabinderServiceClient {
	databinderService, err := rpc.SetupDataBinderService(fmt.Sprintf("localhost:%s", grpcPort))
	if err != nil {
		log.Fatal(fmt.Sprintf("Connection to databinder service failed %q", err))
	}

	_, err = (*databinderService).Init(context.Background(), scanRequest.DatabinderTemplate)
	if err != nil {
		log.Fatal(err.Error())
	}

	return databinderService
}

// Init functions
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
		AnalyzeTemplate: scanRequest.GetAnalyzeTemplate(),
		MinProbability:  scanRequest.GetMinProbability(),
	}

	if err != nil {
		log.Fatal(err.Error())
	}
}

func setupAnoymizerService() {
	anonymizerSvcHost := os.Getenv("ANONYMIZER_SVC_HOST")
	if anonymizerSvcHost == "" {
		log.Fatal("anonymizer service address is empty")
	}

	anonymizerSvcPort := os.Getenv("ANONYMIZER_SVC_PORT")
	if anonymizerSvcPort == "" {
		log.Fatal("anonymizer service port is empty")
	}

	var err error
	anonymizeService, err = rpc.SetupAnonymizeService(anonymizerSvcHost + ":" + anonymizerSvcPort)
	if err != nil {
		log.Error(fmt.Sprintf("Connection to anonymizer service failed %q", err))
	}

	if err != nil {
		log.Fatal(err.Error())
	}
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

func initScanner() {
	godotenv.Load()

	scannerObj := os.Getenv("SCANNER_REQUEST")
	template := &message_types.ScanRequest{}
	err := templates.ConvertJSONToInterface(scannerObj, template)
	if err != nil {
		log.Fatal(fmt.Sprintf("Error formating scanner template %q", err.Error()))
	}
	scanRequest = template
	storageKind = scanRequest.Kind

	if storageKind == "" {
		log.Fatal("storage king var must me set")
	}

	// TODO: Change!!
	grpcPort = os.Getenv("GRPC_PORT")
	if grpcPort == "" {
		// Set to default
		grpcPort = "5000"
	}
}

// analyzeItem checks if the file needs to be scanned.
// Then sends it to the analyzer and updates the cache that it was scanned.
func analyzeItem(cache *cache.Cache,
	uniqueID string,
	analyzeService *message_types.AnalyzeServiceClient,
	analyzeRequest *message_types.AnalyzeRequest,
	item interface{}) (string, []*message_types.AnalyzeResult, error) {
	var err error
	var val string

	err = scannerObj.IsContentSupported(item)
	if err != nil {
		return "", nil, err
	}

	val, err = (*cache).Get(uniqueID)
	if err != nil {
		return "", nil, err
	}

	// Value not found in the cache. Need to scan the file and update the cache
	if val == "" {
		itemContent, err := scannerObj.GetItemContent(item)
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

	// Otherwise skip- item was already scanned
	return "", nil, nil
}
