package databinder

import message_types "github.com/presid-io/presidio-genproto/golang"

// DataBinder represents the binder to the different output types such as SQL and Datawarehouse
type DataBinder interface {
	// Init the specified databinder
	Init()

	// WriteAnalyzeResults write the analyzer results to the specified databinder
	WriteAnalyzeResults(results []*message_types.AnalyzeResult, path string) error

	// WriteAnonymizeResults write the analyzer results to the specified databinder
	WriteAnonymizeResults(result *message_types.AnonymizeResponse, path string) error
}
