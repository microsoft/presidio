package scanner

import (
	message_types "github.com/Microsoft/presidio-genproto/golang"
)

// CreateScanner creates a new instance of the scanner according to the specified kind
func CreateScanner(scanRequest *message_types.ScanRequest) Scanner {
	switch scanRequest.GetKind() {
	case message_types.DatasinkTypesEnum.String(message_types.DatasinkTypesEnum_azureblob), message_types.DatasinkTypesEnum.String(message_types.DatasinkTypesEnum_s3):
		storageScanner := NewStorageScanner(scanRequest.GetKind(), scanRequest.GetCloudStorageConfig())
		return storageScanner
	}
	return nil
	// TODO: ADD HERE NEW STORAGE KINDS

}
