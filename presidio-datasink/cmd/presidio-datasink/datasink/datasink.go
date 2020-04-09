package datasink

import types "github.com/Microsoft/presidio-genproto/golang"

// Datasink represents the different data output types such as SQL and Datawarehouse
type Datasink interface {
	// Init the specified datasink
	Init()

	// WriteAnalyzeResults write the analyzer results to the specified datasink
	WriteAnalyzeResults(results []*types.AnalyzeResult, path string) error

	// WriteAnonymizeResults write the anonymized results to the specified datasink
	WriteAnonymizeResults(result *types.AnonymizeResponse, path string) error
}
