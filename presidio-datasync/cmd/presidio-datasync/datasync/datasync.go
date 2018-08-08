package dataSync

import message_types "github.com/Microsoft/presidio-genproto/golang"

// DataSync represents the Sync to the different output types such as SQL and Datawarehouse
type DataSync interface {
	// Init the specified dataSync
	Init()

	// WriteAnalyzeResults write the analyzer results to the specified dataSync
	WriteAnalyzeResults(results []*message_types.AnalyzeResult, path string) error

	// WriteAnonymizeResults write the analyzer results to the specified dataSync
	WriteAnonymizeResults(result *message_types.AnonymizeResponse, path string) error
}
