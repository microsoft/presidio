package storageScanner

import (
	"fmt"
	"path/filepath"

	"github.com/presid-io/stow"

	log "github.com/Microsoft/presidio/pkg/logger"
	"github.com/Microsoft/presidio/pkg/storage"
	"github.com/Microsoft/presidio/presidio-scanner/cmd/presidio-scanner/item"
)

type storageItem struct {
	item stow.Item
}

func NewItem(item interface{}) item.Item {
	stowItem := item.(stow.Item)
	storageItem := storageItem{item: stowItem}
	return &storageItem
}

func (storageItem *storageItem) GetPath() string {
	return storageItem.item.URL().Path
}

func (storageItem *storageItem) IsContentTypeSupported() error {
	ext := filepath.Ext(storageItem.item.Name())

	if ext != ".txt" && ext != ".csv" && ext != ".json" && ext != ".tsv" {
		return fmt.Errorf("Expected: file extension txt, csv, json, tsv, received: %s", ext)
	}
	return nil
}

func (storageItem *storageItem) GetUniqueID() (string, error) {
	etag, err := storageItem.item.ETag()
	if err != nil {
		log.Error(err.Error())
		return "", err
	}
	return etag, nil
}

// Read the content of the cloud item
func (storageItem *storageItem) GetContent() (string, error) {
	return storage.ReadObject(storageItem.item)
}
