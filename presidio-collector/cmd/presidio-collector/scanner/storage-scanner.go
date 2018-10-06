package scanner

import (
	"github.com/presid-io/stow"

	types "github.com/Microsoft/presidio-genproto/golang"

	log "github.com/Microsoft/presidio/pkg/logger"
	"github.com/Microsoft/presidio/pkg/storage"
)

type storageScanner struct {
	containerName string
	storageAPI    *storage.API
}

// NewStorageScanner returns new instance of DB Data writer
func NewStorageScanner(inputConfig *types.CloudStorageConfig) Scanner {
	scanner := storageScanner{}
	scanner.Init(inputConfig)
	return &scanner
}

func (scanner *storageScanner) Init(cloudStorageConfig *types.CloudStorageConfig) {
	config, containerName, kind, err := storage.Init(cloudStorageConfig)
	if err != nil {
		log.Fatal(err.Error())
	}

	storageAPI, err := storage.New(kind, config, 10)
	if err != nil {
		log.Fatal(err.Error())
	}

	scanner.containerName = containerName
	scanner.storageAPI = storageAPI
}

func (scanner *storageScanner) Scan(walkFunction ScanFunc) error {
	// Get container/bucker reference
	container, err := scanner.storageAPI.CreateContainer(scanner.containerName)
	if err != nil {
		log.Fatal(err.Error())
	}

	var scanErr error
	// Walks over the files in the container/bucket
	// Wrapping the walkFunction as storage.WalkFunc
	err = scanner.storageAPI.WalkFiles(container, func(item stow.Item) {
		scanErr = walkFunction(item)

	})

	return scanErr
}
