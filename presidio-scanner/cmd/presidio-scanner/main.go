package main

import (
	"context"
	"fmt"
	"os"

	"github.com/joho/godotenv"

	message_types "github.com/presid-io/presidio-genproto/golang"
	"github.com/presid-io/presidio/pkg/cache"
	"github.com/presid-io/presidio/pkg/cache/redis"
	kv_consul "github.com/presid-io/presidio/pkg/kv/consul"
	log "github.com/presid-io/presidio/pkg/logger"
	"github.com/presid-io/presidio/pkg/modules/analyzer"
	scanner "github.com/presid-io/presidio/pkg/modules/scanner"
	"github.com/presid-io/presidio/pkg/rpc"
	"github.com/presid-io/presidio/pkg/service-discovery"
	"github.com/presid-io/presidio/pkg/service-discovery/consul"
	"github.com/presid-io/presidio/pkg/templates"
)

var (
	storageKind    string
	analyzeKey     string
	grpcPort       string
	analyzeRequest *message_types.AnalyzeRequest
	analyzerObj    analyzer.Analyzer
	scannerObj     scanner.Scanner
)

func main() {
	// Setup objects
	var err error
	store := consul.New()

	cache := setupCache(store)
	setupAnalyzerObjects(store)
	databinderService := setupDataBinderService()
	scannerObj = createScanner(storageKind)

	err = scannerObj.WalkItems(cache, func(item interface{}) {
		var scanResult []*message_types.AnalyzeResult

		itemPath := scannerObj.GetItemPath(item)
		uniqueID, err := scannerObj.GetItemUniqueID(item)
		if err != nil {
			log.Error(fmt.Sprintf("error getting item unique id: %s, error: %q", itemPath, err.Error()))
			return
		}

		scanResult, err = AnalyzeItem(&cache, uniqueID, &analyzerObj, analyzeRequest, item)
		if err != nil {
			log.Error(fmt.Sprintf("error scanning file: %s, error: %q", itemPath, err.Error()))
			return
		}

		if len(scanResult) > 0 {
			err = sendResultToDataBinder(itemPath, scanResult, cache, databinderService)
			if err != nil {
				log.Error(fmt.Sprintf("error sending file to databinder: %s, error: %q", itemPath, err.Error()))
				return
			}
		}

		writeItemToCache(uniqueID, itemPath, cache)
	})

	if err != nil {
		log.Fatal(err.Error())
	}
}

func writeItemToCache(uniqueID string, scannedPath string, cache cache.Cache) {
	// If writing to databinder succeeded - update the cache
	err := cache.Set(uniqueID, scannedPath)
	if err != nil {
		log.Error(err.Error())
	}
}

func sendResultToDataBinder(scannedPath string, results []*message_types.AnalyzeResult, cache cache.Cache,
	databinderService *message_types.DatabinderServiceClient) error {
	srv := *databinderService

	for _, element := range results {
		// Remove PII from results
		element.Text = ""
	}

	databinderRequest := &message_types.DatabinderRequest{
		AnalyzeResults: results,
		Path:           scannedPath,
	}

	_, err := srv.Apply(context.Background(), databinderRequest)
	if err != nil {
		log.Error(err.Error())
		return err
	}

	return nil
}

func setupDataBinderService() *message_types.DatabinderServiceClient {
	databinderService, err := rpc.SetupDataBinderService(fmt.Sprintf("localhost:%s", grpcPort))
	if err != nil {
		log.Fatal(fmt.Sprintf("Connection to databinder service failed %q", err))
	}
	return databinderService
}

// Init functions
func setupAnalyzerObjects(store sd.Store) {
	var err error
	analyzerSvcHost, err := store.GetService("analyzer")
	if err != nil {
		log.Fatal(fmt.Sprintf("analyzer service address is empty %q", err))
	}

	analyzeService, err := rpc.SetupAnalyzerService(analyzerSvcHost)
	if err != nil {
		log.Fatal(fmt.Sprintf("Connection to analyzer service failed %q", err))
	}

	t := templates.New(kv_consul.New())
	analyzerObj = analyzer.New(analyzeService)
	analyzeRequest, err = analyzer.GetAnalyzeRequest(t, analyzeKey)
	if err != nil {
		log.Fatal(err.Error())
	}
}

func setupCache(store sd.Store) cache.Cache {
	redisService, err := store.GetService("redis")
	if err != nil {
		log.Fatal(err.Error())
	}
	return redis.New(
		redisService,
		"", // no password set TODO: Add password
		0,  // use default DB
	)
}

func init() {
	err := godotenv.Load()
	if err != nil {
		log.Fatal("Error loading .env file")
	}

	grpcPort = os.Getenv("GRPC_PORT")

	storageKind = os.Getenv("STORAGE_KIND")
	analyzeKey = os.Getenv("ANALYZE_KEY")

	if storageKind == "" {
		log.Fatal("STORAGE_KIND env var must me set")
	}

	if grpcPort == "" {
		// Set to default
		grpcPort = "5000"
	}
}

// AnalyzeItem checks if the file needs to be scanned.
// Then sends it to the analyzer and updates the cache that it was scanned.
func AnalyzeItem(cache *cache.Cache,
	uniqueID string,
	analyzerModule *analyzer.Analyzer,
	analyzeRequest *message_types.AnalyzeRequest,
	item interface{}) ([]*message_types.AnalyzeResult, error) {
	var err error
	var val string

	err = scannerObj.IsContentSupported(item)
	if err != nil {
		return nil, err
	}

	val, err = (*cache).Get(uniqueID)
	if err != nil {
		return nil, err
	}

	// Value not found in the cache. Need to scan the file and update the cache
	if val == "" {
		itemContent, err := scannerObj.GetItemContent(item)
		if err != nil {
			log.Error(fmt.Sprintf("error getting item's content, error: %q", err.Error()))
			return nil, err
		}

		results, err := (*analyzerModule).InvokeAnalyze(context.Background(), analyzeRequest, itemContent)
		if err != nil {
			return nil, err
		}

		return results.AnalyzeResults, nil
	}

	// Otherwise skip- item was already scanned
	return nil, nil
}
