package analyzer

import (
	"context"
	"fmt"

	message_types "github.com/presid-io/presidio-genproto/golang"
	helper "github.com/presid-io/presidio/pkg/helper"
	t "github.com/presid-io/presidio/pkg/templates"
)

// Analyzer interface for Invoking
type Analyzer interface {
	InvokeAnalyze(c context.Context, analyzeRequest *message_types.AnalyzeRequest) (*message_types.AnalyzeResponse, error)
}

type analyzer struct {
	analyzeService *message_types.AnalyzeServiceClient
}

// New analyzer struct
func New(analyzeService *message_types.AnalyzeServiceClient) Analyzer {
	return &analyzer{analyzeService: analyzeService}
}

// GetAnalyzeRequest returns analyze request for a specific project and id
func GetAnalyzeRequest(templates *t.Templates, analyzeKey string) (*message_types.AnalyzeRequest, error) {
	template, err := templates.GetTemplate(analyzeKey)

	if err != nil {
		return nil, fmt.Errorf("Failed to retrieve template %q", err)
	}

	analyzeTemplate := &message_types.AnalyzeTemplate{}
	err = helper.ConvertJSONToInterface(template, analyzeTemplate)
	if err != nil {
		return nil, fmt.Errorf("Failed to convert template %q", err)
	}
	analyzeRequest := &message_types.AnalyzeRequest{
		AnalyzeTemplate: analyzeTemplate,
	}

	return analyzeRequest, nil
}

// InvokeAnalyze returns the analyze results
func (analyzer *analyzer) InvokeAnalyze(c context.Context, analyzeRequest *message_types.AnalyzeRequest) (*message_types.AnalyzeResponse, error) {

	srv := *analyzer.analyzeService

	analyzeResponse, err := srv.Apply(c, analyzeRequest)
	if err != nil {
		return nil, err
	}

	return analyzeResponse, nil
}
