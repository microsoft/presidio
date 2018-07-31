package main

import (
	message_types "github.com/Microsoft/presidio-genproto/golang"
	"github.com/Microsoft/presidio/presidio-scanner/cmd/presidio-scanner/scanner"
	storage_scanner "github.com/Microsoft/presidio/presidio-scanner/cmd/presidio-scanner/storage-scanner"
)

func createScanner(scanRequest *message_types.ScanRequest) scanner.Scanner {
	if scanRequest.GetKind() == "s3" || scanRequest.GetKind() == "azure" {
		storageScanner := storage_scanner.New(scanRequest.GetKind(), scanRequest.GetInputConfig())
		return storageScanner
	}
	return nil
	// TODO: ADD HERE NEW STORAGE KINDS

}
