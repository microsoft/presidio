package request

import (
	"context"
	"fmt"

	t "github.com/presidium-io/presidium/pkg/templates"
	message_types "github.com/presidium-io/presidium/pkg/types"
)

// GetAnalyzeRequest returns analyze request for a specific project and id
func GetAnalyzeRequest(templates *t.Templates, analyzeKey string) (*message_types.AnalyzeRequest, error) {
	template, err := templates.GetTemplate(analyzeKey)

	if err != nil {
		return nil, fmt.Errorf("Failed to retrieve template %q", err)
	}

	analyzeRequest := &message_types.AnalyzeRequest{}
	err = t.ConvertJSON2Interface(template, analyzeRequest)

	if err != nil {
		return nil, fmt.Errorf("Failed to convert template %q", err)
	}
	return analyzeRequest, nil
}

// InvokeAnalyze returns the analyze results
func InvokeAnalyze(c context.Context, analyzeService *message_types.AnalyzeServiceClient, analyzeRequest *message_types.AnalyzeRequest, text string) (*message_types.Results, error) {
	analyzeRequest.Value = text
	srv := *analyzeService

	analyzeResult, err := srv.Apply(c, analyzeRequest)
	if err != nil {
		return nil, err
	}

	return analyzeResult, nil
}
