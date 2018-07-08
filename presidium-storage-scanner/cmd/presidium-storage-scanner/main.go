package main

import (
	"context"
	"fmt"
	"log"
	"os"

	"github.com/joho/godotenv"
	"github.com/presidium-io/stow"

	message_types "github.com/presidium-io/presidium-genproto/golang"
	"github.com/presidium-io/presidium/pkg/cache/redis"
	"github.com/presidium-io/presidium/pkg/rpc"
	"github.com/presidium-io/presidium/pkg/service-discovery/consul"
	"github.com/presidium-io/presidium/pkg/storage"
	scanner "github.com/presidium-io/presidium/presidium-storage-scanner/cmd/presidium-storage-scanner/storage-scanner"
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
	databinderService *message_types.DatabinderServiceClient
)

func main() {
	var err error
	store := consul.New()

	var analyzerSvcHost, redisService string
	var analyzeService *message_types.AnalyzeServiceClient

	redisService, err = store.GetService("redis")
	if err != nil {
		log.Fatal(err.Error())
		return
	}

	analyzerSvcHost, err = store.GetService("analyzer")
	if err != nil {
		log.Fatal(fmt.Sprintf("analyzer service address is empty %q", err))
	}

	analyzeService, err = rpc.SetupAnalyzerService(analyzerSvcHost)
	if err != nil {
		log.Fatal(fmt.Sprintf("Connection to analyzer service failed %q", err))
	}

	cache := redis.New(
		redisService,
		"", // no password set
		0,  // use default DB
	)

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

	storageAPI, err := storage.New(cache, storageKind, config, analyzeService)
	if err != nil {
		log.Fatal(err.Error())
		return
	}

	container, err := storageAPI.CreateContainer(containerName)
	if err != nil {
		log.Fatal(err.Error())
		return
	}

	err = storageAPI.WalkFiles(container, scanner.ScanAndAnalyze, analyzeKey, sendAnalyzeResult)
	if err != nil {
		log.Fatal(err.Error())
		return
	}
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

func sendAnalyzeResult(results []*message_types.AnalyzeResult, path string) {
	srv := *databinderService

	for _, element := range results {
		// Remove PII from results
		element.Text = ""
	}

	databinderRequest := &message_types.DatabinderRequest{
		AnalyzeResults: results,
		Path:           path,
	}

	databinderResponse, err := srv.Apply(context.Background(), databinderRequest)
	if err != nil {
		log.Println("ERROR:", err)
	}
	log.Println(databinderResponse)
}
