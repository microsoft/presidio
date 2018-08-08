package cloudStorage

import (
	"fmt"
	"path/filepath"

	"github.com/presid-io/stow"

	message_types "github.com/Microsoft/presidio-genproto/golang"
	log "github.com/Microsoft/presidio/pkg/logger"
	"github.com/Microsoft/presidio/pkg/storage"
	"github.com/Microsoft/presidio/pkg/templates"
	"github.com/Microsoft/presidio/presidio-datasync/cmd/presidio-datasync/datasync"
)

type cloudStorageDataSync struct {
	kind               string
	cloudStorageConfig *message_types.CloudStorageConfig
	container          stow.Container
}

// New returns new instance of DB Data writter
func New(datasync *message_types.DataSync, kind string) dataSync.DataSync {
	db := cloudStorageDataSync{kind: kind, cloudStorageConfig: datasync.GetCloudStorageConfig()}
	db.Init()
	return &db
}

func (dataSync *cloudStorageDataSync) Init() {
	config, containerName, err := storage.Init(dataSync.kind, dataSync.cloudStorageConfig)
	if err != nil {
		log.Fatal("Unknown storage kind")
	}

	storageAPI, err := storage.New(dataSync.kind, config, 10)
	if err != nil {
		log.Fatal(err.Error())
	}

	// Get container/bucker reference
	container, err := storageAPI.CreateContainer(containerName)
	if err != nil {
		log.Fatal(err.Error())
	}

	dataSync.container = container
}

func (dataSync *cloudStorageDataSync) WriteAnalyzeResults(results []*message_types.AnalyzeResult, path string) error {
	resultString, err := templates.ConvertInterfaceToJSON(results)
	if err != nil {
		log.Error(err.Error())
		return err
	}

	err = storage.PutItem(addActionToFilePath(path, "analyzed"), resultString, dataSync.container)
	if err != nil {
		log.Error(err.Error())
		return err
	}

	log.Info(fmt.Sprintf("%d rows were written to the cloud storage successfully", len(results)))
	return nil
}

func (dataSync *cloudStorageDataSync) WriteAnonymizeResults(result *message_types.AnonymizeResponse, path string) error {
	err := storage.PutItem(addActionToFilePath(path, "anonymized"), result.Text, dataSync.container)
	if err != nil {
		log.Error(err.Error())
		return err
	}

	log.Info("Analyzed result was written to the cloud storage successfully")
	return nil
}

func addActionToFilePath(path string, action string) string {
	ext := filepath.Ext(path)
	path = path[:len(path)-len(ext)]
	if string(path[0]) == "/" {
		path = path[1:]
	}
	return fmt.Sprintf("%s-%s%s", path, action, ext)
}
