package main

import (
	"context"
	"fmt"
	"log"
	"os"

	"github.com/joho/godotenv"
	"github.com/presidium-io/stow"

	message_types "github.com/presidium-io/presidium-genproto/golang"
	"github.com/presidium-io/presidium/pkg/cache"
	"github.com/presidium-io/presidium/pkg/cache/redis"
	kv_consul "github.com/presidium-io/presidium/pkg/kv/consul"
	"github.com/presidium-io/presidium/pkg/modules/analyzer"
	"github.com/presidium-io/presidium/pkg/rpc"
	"github.com/presidium-io/presidium/pkg/service-discovery"
	"github.com/presidium-io/presidium/pkg/service-discovery/consul"
	"github.com/presidium-io/presidium/pkg/storage"
	"github.com/presidium-io/presidium/pkg/templates"
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

	storageKind    string
	analyzeKey     string
	grpcPort       string
	analyzeRequest *message_types.AnalyzeRequest
	analyzerObj    analyzer.Analyzer
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
	cache := setupCache(store)
	setupAnalyzerObjects(store)

	storageAPI, err := storage.New(cache, storageKind, containerSettings.config)
	if err != nil {
		log.Fatal(err.Error())
	}

	// Get container/bucker reference
	container, err := storageAPI.CreateContainer(containerSettings.name)
	if err != nil {
		log.Fatal(err.Error())
	}

	databinderService := setupDataBinderService()

	// Walks over the files in the container/bucket
	err = storageAPI.WalkFiles(container, func(item stow.Item) {
		scanResult := ScanAndAnalyze(&cache, item, &analyzerObj, analyzeRequest)
		if len(scanResult) > 0 {
			sendResultToDataBinder(item, scanResult, cache, databinderService)
		}
	})

	if err != nil {
		log.Fatal(err.Error())
	}
}

func sendResultToDataBinder(item stow.Item, results []*message_types.AnalyzeResult, cache cache.Cache,
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
		return
	}

	// If writing to databinder succeded - update the cache
	etag, err := item.ETag()
	if err != nil {
		log.Println("ERROR:", err)
		return
	}

	err = cache.Set(etag, item.Name())
	if err != nil {
		log.Println("ERROR:", err)
	}
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
