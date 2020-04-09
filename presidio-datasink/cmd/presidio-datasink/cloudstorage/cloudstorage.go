package cloudStorage

import (
	"fmt"
	"path/filepath"

	"github.com/presid-io/stow"

	types "github.com/Microsoft/presidio-genproto/golang"

	log "github.com/Microsoft/presidio/pkg/logger"
	"github.com/Microsoft/presidio/pkg/presidio"
	"github.com/Microsoft/presidio/pkg/storage"
	"github.com/Microsoft/presidio/presidio-datasink/cmd/presidio-datasink/datasink"
)

type cloudStorageDatasink struct {
	cloudStorageConfig *types.CloudStorageConfig
	container          stow.Container
}

// New returns new instance of DB Data writer
func New(datasink *types.Datasink) datasink.Datasink {
	db := cloudStorageDatasink{cloudStorageConfig: datasink.GetCloudStorageConfig()}
	db.Init()
	return &db
}

func (datasink *cloudStorageDatasink) Init() {
	config, containerName, kind, err := storage.Init(datasink.cloudStorageConfig)
	if err != nil {
		log.Fatal(err.Error())
	}

	storageAPI, err := storage.New(kind, config, 10)
	if err != nil {
		log.Fatal(err.Error())
	}

	// Get container/bucket reference
	container, err := storageAPI.CreateContainer(containerName)
	if err != nil {
		log.Fatal(err.Error())
	}

	datasink.container = container
}

func (datasink *cloudStorageDatasink) WriteAnalyzeResults(results []*types.AnalyzeResult, path string) error {
	resultString, err := presidio.ConvertInterfaceToJSON(results)
	if err != nil {
		return err
	}

	err = storage.PutItem(addSuffixToPath(path, "analyzed"), resultString, datasink.container)
	if err != nil {
		return err
	}

	log.Info("%d rows were written to the cloud storage successfully", len(results))
	return nil
}

func (datasink *cloudStorageDatasink) WriteAnonymizeResults(result *types.AnonymizeResponse, path string) error {
	err := storage.PutItem(addSuffixToPath(path, "anonymized"), result.Text, datasink.container)
	if err != nil {
		return err
	}

	log.Info("Analyzed result was written to the cloud storage successfully")
	return nil
}

func addSuffixToPath(path string, suffix string) string {
	// Get file extension
	ext := filepath.Ext(path)
	// Get path without file extension
	path = path[:len(path)-len(ext)]
	if string(path[0]) == "/" {
		path = path[1:]
	}
	// Add suffix to path and put back the extension
	return fmt.Sprintf("%s-%s%s", path, suffix, ext)
}
