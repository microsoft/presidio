package storageScanner

import (
	"fmt"
	"path/filepath"

	"github.com/presid-io/stow"

	message_types "github.com/presid-io/presidio-genproto/golang"
	log "github.com/presid-io/presidio/pkg/logger"
	"github.com/presid-io/presidio/pkg/storage"
	"github.com/presid-io/presidio/presidio-scanner/cmd/presidio-scanner/scanner"
)

type storageScanner struct {
	kind          string
	containerName string
	config        stow.ConfigMap
}

// New returns new instance of DB Data writter
func New(kind string, inputConfig *message_types.CloudStorageConfig) scanner.Scanner {
	scanner := storageScanner{kind: kind}
	scanner.Init(inputConfig)
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

func (scanner *storageScanner) Init(inputConfig *message_types.CloudStorageConfig) {
	switch scanner.kind {
	case message_types.DataBinderTypesEnum.String(message_types.DataBinderTypesEnum_azureblob):
		scanner.config, scanner.containerName = storage.InitBlobStorage(inputConfig)
	case message_types.DataBinderTypesEnum.String(message_types.DataBinderTypesEnum_s3):
		scanner.config, scanner.containerName = storage.InitS3(inputConfig)
	// case "google":
	// 	// Add support
	default:
		log.Fatal("Unknown storage kind")
	}
}

// Read the content of the cloud item
func (scanner *storageScanner) GetItemContent(input interface{}) (string, error) {
	// cast to stow item
	stowInput := input.(stow.Item)
	return storage.ReadObject(stowInput)
}

func (scanner *storageScanner) WalkItems(walkFunction scanner.WalkFunc) error {
	storageAPI, err := storage.New(scanner.kind, scanner.config, 10)
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
