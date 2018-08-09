package datasink

import message_types "github.com/Microsoft/presidio-genproto/golang"

// Datasink represents the different data output types such as SQL and Datawarehouse
type Datasink interface {
	// Init the specified datasink
	Init()

	// WriteAnalyzeResults write the analyzer results to the specified datasink
	WriteAnalyzeResults(results []*message_types.AnalyzeResult, path string) error

	// WriteAnonymizeResults write the analyzer results to the specified datasink
	WriteAnonymizeResults(result *message_types.AnonymizeResponse, path string) error
}
