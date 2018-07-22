package main

import (
	"fmt"

	"os"

	"github.com/joho/godotenv"
	"github.com/presid-io/stow"

	log "github.com/presid-io/presidio/pkg/logger"

	message_types "github.com/presid-io/presidio-genproto/golang"
	"github.com/presid-io/presidio/pkg/cache/redis"
	"github.com/presid-io/presidio/pkg/platform/kube"
	"github.com/presid-io/presidio/pkg/rpc"
	"github.com/presid-io/presidio/pkg/storage"
	scanner "github.com/presid-io/presidio/presidio-storage-scanner/cmd/presidio-storage-scanner/storage-scanner"
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
	analyzeKey  string
	namespace   = os.Getenv("presidio_NAMESPACE")
)

const (
	envKubeConfig = "KUBECONFIG"
)

func main() {
	var err error

	var analyzeService *message_types.AnalyzeServiceClient

	redisHost := os.Getenv("REDIS_HOST")
	if redisHost == "" {
		log.Fatal("redis address is empty")
	}

	redisPort := os.Getenv("REDIS_SVC_PORT")
	if redisPort == "" {
		log.Fatal("redis port is empty")
	}

	redisAddress := redisHost + ":" + redisPort

	analyzerSvcHost := os.Getenv("ANALYZER_SVC_HOST")
	if analyzerSvcHost == "" {
		log.Fatal("analyzer service address is empty")
	}

	analyzerSvcPort := os.Getenv("ANALYZER_SVC_PORT")
	if analyzerSvcPort == "" {
		log.Fatal("analyzer service port is empty")
	}

	analyzeService, err = rpc.SetupAnalyzerService(analyzerSvcHost + ":" + analyzerSvcPort)
	if err != nil {
		log.Error(fmt.Sprintf("Connection to analyzer service failed %q", err))
	}

	cache := redis.New(
		redisAddress,
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
	}

	container, err := storageAPI.CreateContainer(containerName)
	if err != nil {
		log.Fatal(err.Error())
	}

	store, err := kube.New(namespace, "", kubeConfigPath())
	if err != nil {
		log.Fatal(err.Error())

	}

	err = storageAPI.WalkFiles(container, scanner.ScanAndAnalyze, analyzeKey, store)
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
	analyzeKey = os.Getenv("ANALYZE_KEY")

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

func kubeConfigPath() string {
	if v, ok := os.LookupEnv(envKubeConfig); ok {
		return v
	}
	defConfig := os.ExpandEnv("$HOME/.kube/config")
	if _, err := os.Stat(defConfig); err == nil {
		log.Info("Using config from " + defConfig)
		return defConfig
	}

	// If we get here, we might be in-Pod.
	return ""
}
