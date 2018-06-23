package scanner

import (
	types "github.com/Microsoft/presidio-genproto/golang"
)

// ScanFunc is the function the is executed on the scanned item
type ScanFunc func(item interface{}) error

// Scanner interface represent the supported scanner methods.
type Scanner interface {
	//Init the scanner
	Init(inputConfig *types.CloudStorageConfig)

	//Scan walks over the items to scan and executes ScanFunc on each of the items
	Scan(fn ScanFunc) error
}
