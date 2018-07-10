package main

import (
	"context"
	"fmt"
	"log"
	"os"

	"github.com/joho/godotenv"
	message_types "github.com/presidium-io/presidium-genproto/golang"
	c "github.com/presidium-io/presidium/pkg/cache"
	"github.com/presidium-io/presidium/pkg/cache/redis"
	kv_consul "github.com/presidium-io/presidium/pkg/kv/consul"
	"github.com/presidium-io/presidium/pkg/modules/analyzer"
	"github.com/presidium-io/presidium/pkg/rpc"
	"github.com/presidium-io/presidium/pkg/service-discovery"
	"github.com/presidium-io/presidium/pkg/service-discovery/consul"
	"github.com/presidium-io/presidium/pkg/storage"
	"github.com/presidium-io/presidium/pkg/templates"
	"github.com/presidium-io/stow"
)

var (
	// Azure Parameters
	azureAccountName string
	azureAccountKey  string
	azureContainer   string

	// S3 Parameters
	s3AccessKeyID string
	s3SecretKey   string
	s3Region      string
	s3Bucket      string

	storageKind       string
	analyzeKey        string
	grpcPort          string
	cache             c.Cache
	databinderService *message_types.DatabinderServiceClient
	analyzeRequest    *message_types.AnalyzeRequest
	analyzerObj       analyzer.Analyzer
	analyzeService    *message_types.AnalyzeServiceClient
)

type storageSettings struct {
	name   string
	config stow.ConfigMap
}

func main() {
	// Setup objects
	var err error
	store := consul.New()

	containerSettings := setupStorage()
	analyzeService = setupAnalyzerService(store)
	cache = setupCache(store)
	setupAnalyzerObjects()

	storageAPI, err := storage.New(cache, storageKind, containerSettings.config)
	if err != nil {
		log.Fatal(err.Error())
		return
	}

	// Get container/bucker reference
	container, err := storageAPI.CreateContainer(containerSettings.name)
	if err != nil {
		log.Fatal(err.Error())
		return
	}

	// Walks over the files in the container/bucket
	err = storageAPI.WalkFiles(container, handleContainerItem)
	if err != nil {
		log.Fatal(err.Error())
		return
	}
}

// handleContainerItem will check if the item needs scanning (if it's not in the cache)
// it will send them to Analyzer and will send the results to the databinder
func handleContainerItem(item stow.Item) {
	scanResult := ScanAndAnalyze(&cache, item, &analyzerObj, analyzeRequest)
	if len(scanResult) > 0 {
		sendResultToDataBinder(item, scanResult, cache, databinderService)
	}
}

func sendResultToDataBinder(item stow.Item, results []*message_types.AnalyzeResult, cache c.Cache,
	databinderService *message_types.DatabinderServiceClient) {
	srv := *databinderService

	for _, element := range results {
		// Remove PII from results
		element.Text = ""
	}

	databinderRequest := &message_types.DatabinderRequest{
		AnalyzeResults: results,
		Path:           item.URL().Path,
	}

	_, err := srv.Apply(context.Background(), databinderRequest)
	if err != nil {
		log.Println("ERROR:", err)
		// If writing to databinder failed - delete the item from cache so it will be scanned again on the next run
		etag, err := item.ETag()
		if err != nil {
			log.Println("ERROR:", err)
		} else {
			cache.Delete(etag)
		}
	}
}

func setupAnalyzerObjects() {
	var err error
	t := templates.New(kv_consul.New())
	analyzerObj = analyzer.New(analyzeService)
	analyzeRequest, err = analyzer.GetAnalyzeRequest(t, analyzeKey)
	if err != nil {
		log.Fatal(err.Error())
		return
	}
}

// Init functions
func setupAnalyzerService(store sd.Store) *message_types.AnalyzeServiceClient {
	analyzerSvcHost, err := store.GetService("analyzer")
	if err != nil {
		log.Fatal(fmt.Sprintf("analyzer service address is empty %q", err))
	}

	analyzeService, err := rpc.SetupAnalyzerService(analyzerSvcHost)
	if err != nil {
		log.Fatal(fmt.Sprintf("Connection to analyzer service failed %q", err))
	}

	return analyzeService
}

func setupCache(store sd.Store) c.Cache {
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

func setupStorage() storageSettings {
	var config stow.ConfigMap
	var containerName string
	switch storageKind {
	case "azure":
		_, config = storage.CreateAzureConfig(azureAccountName, azureAccountKey)
		containerName = azureContainer
	case "s3":
		_, config = storage.CreateS3Config(s3AccessKeyID, s3SecretKey, s3Region)
		containerName = s3Bucket
	// case "google":
	// 	// Add support
	default:
		log.Fatal("Unknown storage kind")
	}

	return storageSettings{name: containerName, config: config}
}

func init() {
	err := godotenv.Load()
	if err != nil {
		log.Fatal("Error loading .env file")
	}

	azureAccountName = os.Getenv("AZURE_ACCOUNT")
	azureAccountKey = os.Getenv("AZURE_KEY")
	azureContainer = os.Getenv("AZURE_CONTAINER")
	grpcPort = os.Getenv("GRPC_PORT")

	s3AccessKeyID = os.Getenv("S3_ACCESS_KEY_ID")
	s3SecretKey = os.Getenv("S3_SECRET_KEY")
	s3Region = os.Getenv("S3_REGION")
	s3Bucket = os.Getenv("S3_BUCKET")

	storageKind = os.Getenv("STORAGE_KIND")
	analyzeKey = os.Getenv("ANALYZE_KEY")

	if storageKind == "" {
		log.Fatal("STORAGE_KIND env var must me set")
	}

	if grpcPort == "" {
		// Set to default
		grpcPort = "5000"
	}

	databinderService, err = rpc.SetupDataBinderService(fmt.Sprintf("localhost:%s", grpcPort))
	if err != nil {
		log.Fatal(fmt.Sprintf("Connection to databinder service failed %q", err))
	}

	switch storageKind {
	case "azure":
		validateAzureConnection(azureAccountName, azureAccountKey, azureContainer)
	case "s3":
		validateS3Connection(s3AccessKeyID, s3SecretKey, s3Region, s3Bucket)
		// TODO: Add case for google
	}
}

func validateAzureConnection(azureAccountKey string, azureAccountName string, azureContainer string) {
	if azureAccountKey == "" || azureAccountName == "" || azureContainer == "" {
		log.Fatal("AZURE_ACCOUNT, AZURE_KEY, AZURE_CONTAINER env vars must me set.")
	}
}

func validateS3Connection(s3AccessKeyID string, s3SecretKey string, s3Region string, s3Bucket string) {
	if s3AccessKeyID == "" || s3SecretKey == "" || s3Region == "" || s3Bucket == "" {
		log.Fatal("S3_ACCESS_KEY_ID, S3_SECRET_KEY, S3_REGION, S3_BUCKET env vars must me set.")
	}
}
