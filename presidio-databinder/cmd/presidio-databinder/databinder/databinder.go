package databinder

import message_types "github.com/presid-io/presidio-genproto/golang"

// DataBinder represents the binder to the different output types such as SQL and Datawarehouse
type DataBinder interface {
	// Init the specified databinder
	Init()

	// WriteResults write the analyzer results to the specified databinder
	WriteResults(results []*message_types.AnalyzeResult, path string) error
}
