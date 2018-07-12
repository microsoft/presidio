package databinder

import message_types "github.com/presid-io/presidio-genproto/golang"

type DataBinder interface {
	Init()
	WriteResults(results []*message_types.AnalyzeResult, path string) error
}
