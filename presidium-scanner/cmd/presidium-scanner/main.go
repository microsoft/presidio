package main

import (
	"fmt"
	"log"
	"os"

	"github.com/graymeta/stow"
	"github.com/joho/godotenv"
	"github.com/presidium-io/presidium/pkg/cache/redis"
	"github.com/presidium-io/presidium/pkg/rpc"
	"github.com/presidium-io/presidium/pkg/service-discovery/consul"
	"github.com/presidium-io/presidium/pkg/storage"
	message_types "github.com/presidium-io/presidium/pkg/types"
	"github.com/presidium-io/presidium/presidium-scanner/cmd/presidium-scanner/scanner"
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

	storageKind string
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

	api, err := storage.New(cache, storageKind, config, analyzeService)
	if err != nil {
		log.Fatal(err.Error())
		return
	}

	container, err := api.CreateContainer(containerName)
	if err != nil {
		log.Fatal(err.Error())
		return
	}

	err = api.WalkFiles(container, scanner.ScanAndAnalyze)
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

	s3AccessKeyID = os.Getenv("S3_ACCESS_KEY_ID")
	s3SecretKey = os.Getenv("S3_SECRET_KEY")
	s3Region = os.Getenv("S3_REGION")
	s3Bucket = os.Getenv("S3_BUCKET")

	storageKind = os.Getenv("STORAGE_KIND")

	if storageKind == "" {
		log.Fatal("STORAGE_KIND env var must me set")
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
