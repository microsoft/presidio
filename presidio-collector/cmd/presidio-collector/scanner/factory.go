package scanner

import (
	types "github.com/Microsoft/presidio-genproto/golang"
)

// CreateScanner creates a new instance of the scanner according to the specified kind
func CreateScanner(scanRequest *types.ScanRequest) Scanner {
	if scanRequest.GetScanTemplate().GetCloudStorageConfig() != nil {
		storageScanner := NewStorageScanner(scanRequest.GetScanTemplate().GetCloudStorageConfig())
		return storageScanner
	}
	// TODO: ADD HERE NEW STORAGE KINDS

	return nil

}
