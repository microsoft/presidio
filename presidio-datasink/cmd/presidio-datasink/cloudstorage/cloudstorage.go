package cloudStorage

import (
	"fmt"
	"path/filepath"

	"github.com/presid-io/stow"

	message_types "github.com/Microsoft/presidio-genproto/golang"
	log "github.com/Microsoft/presidio/pkg/logger"
	"github.com/Microsoft/presidio/pkg/storage"
	"github.com/Microsoft/presidio/pkg/templates"
	"github.com/Microsoft/presidio/presidio-datasink/cmd/presidio-datasink/datasink"
)

type cloudStorageDatasink struct {
	kind               string
	cloudStorageConfig *message_types.CloudStorageConfig
	container          stow.Container
}

// New returns new instance of DB Data writter
func New(datasink *message_types.Datasink, kind string) datasink.Datasink {
	db := cloudStorageDatasink{kind: kind, cloudStorageConfig: datasink.GetCloudStorageConfig()}
	db.Init()
	return &db
}

func (datasink *cloudStorageDatasink) Init() {
	config, containerName, err := storage.Init(datasink.kind, datasink.cloudStorageConfig)
	if err != nil {
		log.Fatal("Unknown storage kind")
	}

	storageAPI, err := storage.New(datasink.kind, config, 10)
	if err != nil {
		log.Fatal(err.Error())
	}

	// Get container/bucker reference
	container, err := storageAPI.CreateContainer(containerName)
	if err != nil {
		log.Fatal(err.Error())
	}

	datasink.container = container
}

func (datasink *cloudStorageDatasink) WriteAnalyzeResults(results []*message_types.AnalyzeResult, path string) error {
	resultString, err := templates.ConvertInterfaceToJSON(results)
	if err != nil {
		log.Error(err.Error())
		return err
	}

	err = storage.PutItem(addActionToFilePath(path, "analyzed"), resultString, datasink.container)
	if err != nil {
		log.Error(err.Error())
		return err
	}

	log.Info("%d rows were written to the cloud storage successfully", len(results))
	return nil
}

func (datasink *cloudStorageDatasink) WriteAnonymizeResults(result *message_types.AnonymizeResponse, path string) error {
	err := storage.PutItem(addActionToFilePath(path, "anonymized"), result.Text, datasink.container)
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
