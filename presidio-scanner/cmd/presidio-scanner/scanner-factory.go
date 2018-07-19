package main

import (
	message_types "github.com/presid-io/presidio-genproto/golang"
	"github.com/presid-io/presidio/presidio-scanner/cmd/presidio-scanner/scanner"
	storage_scanner "github.com/presid-io/presidio/presidio-scanner/cmd/presidio-scanner/storage-scanner"
)

func createScanner(scannerTemplate *message_types.ScannerTemplate) scanner.Scanner {
	if scannerTemplate.GetKind() == "s3" || scannerTemplate.GetKind() == "azure" {
		storageScanner := storage_scanner.New(scannerTemplate.GetKind(), scannerTemplate.GetInputConfig())
		return storageScanner
	}
	return nil
	// TODO: ADD HERE NEW STORAGE KINDS

}
