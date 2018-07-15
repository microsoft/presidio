package storageScanner

import (
	"bytes"
	"fmt"
	"os"
	"path/filepath"

	"github.com/joho/godotenv"
	"github.com/presid-io/stow"

	"github.com/presid-io/presidio/pkg/cache"
	log "github.com/presid-io/presidio/pkg/logger"
	scanner "github.com/presid-io/presidio/pkg/modules/scanner"
	"github.com/presid-io/presidio/pkg/storage"
)

type storageScanner struct {
	kind          string
	containerName string
	config        stow.ConfigMap
}

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
)

// New returns new instance of DB Data writter
func New(kind string) scanner.Scanner {
	scanner := storageScanner{kind: kind}
	return &scanner
}

func (scanner *storageScanner) GetItemPath(input interface{}) string {
	// cast to stow item
	stowInput := input.(stow.Item)
	return stowInput.URL().Path
}

func (scanner *storageScanner) IsContentSupported(input interface{}) error {
	// Check if file type supported
	// cast to stow item
	stowInput := input.(stow.Item)
	ext := filepath.Ext(stowInput.Name())

	if ext != ".txt" && ext != ".csv" && ext != ".json" && ext != ".tsv" {
		return fmt.Errorf("Expected: file extension txt, csv, json, tsv, received: %s", ext)
	}
	return nil
}

func (scanner *storageScanner) GetItemUniqueID(input interface{}) (string, error) {
	// cast to stow item
	stowInput := input.(stow.Item)
	etag, err := stowInput.ETag()
	if err != nil {
		log.Error(err.Error())
		return "", err
	}
	return etag, nil
}

func (scanner *storageScanner) Init() {
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

	switch scanner.kind {
	case "azure":
		validateAzureConnection(azureAccountName, azureAccountKey, azureContainer)
	case "s3":
		validateS3Connection(s3AccessKeyID, s3SecretKey, s3Region, s3Bucket)
		// TODO: Add case for google
	}

	scanner.setupStorage()
}

// Read the content of the cloud item
func (scanner *storageScanner) GetItemContent(input interface{}) (string, error) {
	// cast to stow item
	stowInput := input.(stow.Item)
	reader, err := stowInput.Open()
	if err != nil {
		return "", err
	}

	buf := new(bytes.Buffer)

	if _, err = buf.ReadFrom(reader); err != nil {
		return "", err
	}

	fileContent := buf.String()
	err = reader.Close()

	return fileContent, err
}

func (scanner *storageScanner) WalkItems(cache cache.Cache, walkFunction scanner.WalkFunc) error {
	storageAPI, err := storage.New(cache, scanner.kind, scanner.config)
	if err != nil {
		log.Fatal(err.Error())
	}

	// Get container/bucker reference
	container, err := storageAPI.CreateContainer(scanner.containerName)
	if err != nil {
		log.Fatal(err.Error())
	}

	// Walks over the files in the container/bucket
	// Wrapping the walkFunction as storage.WalkFunc
	err = storageAPI.WalkFiles(container, func(item stow.Item) {
		walkFunction(item)
	})

	return err
}

func (scanner *storageScanner) setupStorage() {
	var config stow.ConfigMap
	var containerName string
	switch scanner.kind {
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

	scanner.config = config
	scanner.containerName = containerName
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
