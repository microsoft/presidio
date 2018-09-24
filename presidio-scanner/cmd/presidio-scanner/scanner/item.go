package scanner

import (
	types "github.com/Microsoft/presidio-genproto/golang"
)

// Item interface represent the supported item's methods.
type Item interface {

	//GetUniqueID returns the scanned item unique id
	GetUniqueID() (string, error)

	//GetContent returns the content of the scanned item
	GetContent() (string, error)

	//GetPath returns the item path
	GetPath() string

	//IsContentTypeSupported returns if the item can be scanned.
	IsContentTypeSupported() error
}

// CreateItem creates a new instance of scanned item according to the specified kind
func CreateItem(scanRequest *types.ScanRequest, item interface{}) Item {
	if scanRequest.GetScanTemplate().GetCloudStorageConfig() != nil {
		storageItem := NewStorageItem(item)
		return storageItem
	}
	return nil
	// TODO: ADD HERE NEW STORAGE KINDS
}
