package scanner

import (
	"github.com/presid-io/stow"

	message_types "github.com/Microsoft/presidio-genproto/golang"
	log "github.com/Microsoft/presidio/pkg/logger"
	"github.com/Microsoft/presidio/pkg/storage"
)

type storageScanner struct {
	kind          string
	containerName string
	storageAPI    *storage.API
}

// NewStorageScanner returns new instance of DB Data writter
func NewStorageScanner(kind string, inputConfig *message_types.CloudStorageConfig) Scanner {
	scanner := storageScanner{kind: kind}
	scanner.Init(inputConfig)
	return &scanner
}

func (scanner *storageScanner) Init(cloudStorageConfig *message_types.CloudStorageConfig) {
	config, containerName, err := storage.Init(scanner.kind, cloudStorageConfig)
	if err != nil {
		log.Fatal("Unknown storage kind")
	}

	storageAPI, err := storage.New(scanner.kind, config, 10)
	if err != nil {
		log.Fatal(err.Error())
	}

	scanner.containerName = containerName
	scanner.storageAPI = storageAPI
}

func (scanner *storageScanner) Scan(walkFunction ScanFunc) (int, error) {
	// Get container/bucker reference
	container, err := scanner.storageAPI.CreateContainer(scanner.containerName)
	if err != nil {
		log.Fatal(err.Error())
	}

	n := 0
	var scanErr error
	// Walks over the files in the container/bucket
	// Wrapping the walkFunction as storage.WalkFunc
	err = scanner.storageAPI.WalkFiles(container, func(item stow.Item) {
		var resultNumber int
		resultNumber, scanErr = walkFunction(item)
		n += resultNumber
	})

	return n, scanErr
}
