package main

import (
	message_types "github.com/presid-io/presidio-genproto/golang"
	"github.com/presid-io/presidio/presidio-scanner/cmd/presidio-scanner/scanner"
	storage_scanner "github.com/presid-io/presidio/presidio-scanner/cmd/presidio-scanner/storage-scanner"
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
