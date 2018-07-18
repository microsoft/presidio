package main

import (
	"github.com/presid-io/presidio/presidio-scanner/cmd/presidio-scanner/scanner"
	storage_scanner "github.com/presid-io/presidio/presidio-scanner/cmd/presidio-scanner/storage-scanner"
)

func createScanner(scannerKind string) scanner.Scanner {
	if scannerKind == "s3" || scannerKind == "azure" {
		storageScanner := storage_scanner.New(scannerKind)
		storageScanner.Init()
		return storageScanner
	}
	return nil
	// TODO: ADD HERE NEW STORAGE KINDS

}
