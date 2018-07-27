package main

import (
	message_types "github.com/presid-io/presidio-genproto/golang"
	"github.com/presid-io/presidio/presidio-scanner/cmd/presidio-scanner/scanner"
	storage_scanner "github.com/presid-io/presidio/presidio-scanner/cmd/presidio-scanner/storage-scanner"
)

func createScanner(scanRequest *message_types.ScanRequest) scanner.Scanner {
	if scanRequest.GetKind() == "s3" || scanRequest.GetKind() == "azure" {
		storageScanner := storage_scanner.New(scanRequest.GetKind(), scanRequest.GetInputConfig())
		return storageScanner
	}
	return nil
	// TODO: ADD HERE NEW STORAGE KINDS

}
