package main

import (
	message_types "github.com/Microsoft/presidio-genproto/golang"
	"github.com/Microsoft/presidio/presidio-scanner/cmd/presidio-scanner/item"
	"github.com/Microsoft/presidio/presidio-scanner/cmd/presidio-scanner/scanner"
	storage_scanner "github.com/Microsoft/presidio/presidio-scanner/cmd/presidio-scanner/storage-scanner"
)

func createScanner(scanRequest *message_types.ScanRequest) scanner.Scanner {
	switch scanRequest.GetKind() {
	case message_types.DataBinderTypesEnum.String(message_types.DataBinderTypesEnum_azureblob), message_types.DataBinderTypesEnum.String(message_types.DataBinderTypesEnum_s3):
		storageScanner := storage_scanner.New(scanRequest.GetKind(), scanRequest.GetCloudStorageConfig())
		return storageScanner
	}
	return nil
	// TODO: ADD HERE NEW STORAGE KINDS

}

func createItem(kind string, item interface{}) item.Item {
	switch kind {
	case message_types.DataBinderTypesEnum.String(message_types.DataBinderTypesEnum_azureblob), message_types.DataBinderTypesEnum.String(message_types.DataBinderTypesEnum_s3):
		storageItem := storage_scanner.NewItem(item)
		return storageItem
	}
	return nil
	// TODO: ADD HERE NEW STORAGE KINDS
}
