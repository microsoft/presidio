package analyze

import (
	"context"
	"fmt"

	types "github.com/Microsoft/presidio-genproto/golang"
	store "github.com/Microsoft/presidio/presidio-api/cmd/presidio-api/api"
	"github.com/Microsoft/presidio/presidio-api/cmd/presidio-api/api/templates"
)

//Analyze text
func Analyze(ctx context.Context, api *store.API, analyzeAPIRequest *types.AnalyzeApiRequest, project string) (*types.AnalyzeResponse, error) {
	switch {
	case analyzeAPIRequest.AnalyzeTemplateId == "" && analyzeAPIRequest.AnalyzeTemplate == nil:
		return nil, fmt.Errorf("Analyze template is missing or empty")
	case analyzeAPIRequest.AnalyzeTemplateId != "" && analyzeAPIRequest.AnalyzeTemplate != nil:
		return nil, fmt.Errorf("Analyze template and Analyze template ID are mutually exclusive")
	case analyzeAPIRequest.AnalyzeTemplate == nil:
		analyzeAPIRequest.AnalyzeTemplate = &types.AnalyzeTemplate{}
	}

	err := templates.GetTemplate(api, project, store.Analyze, analyzeAPIRequest.AnalyzeTemplateId, analyzeAPIRequest.AnalyzeTemplate)
	if err != nil {
		return nil, err
	}

	res, err := api.Services.AnalyzeItem(ctx, analyzeAPIRequest.Text, analyzeAPIRequest.AnalyzeTemplate)
	if err != nil {
		return nil, err
	}
	if res == nil {
		return &types.AnalyzeResponse{}, err
	}
	return res, err

}
