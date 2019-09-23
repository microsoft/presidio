package anonymize

import (
	"context"
	"fmt"

	types "github.com/Microsoft/presidio-genproto/golang"
	store "github.com/Microsoft/presidio/presidio-api/cmd/presidio-api/api"
	"github.com/Microsoft/presidio/presidio-api/cmd/presidio-api/api/templates"
)

//Anonymize text
func Anonymize(ctx context.Context, api *store.API, anonymizeAPIRequest *types.AnonymizeApiRequest, project string) (*types.AnonymizeResponse, error) {

	err := validateTemplate(anonymizeAPIRequest)
	if err != nil {
		return nil, err
	}

	err = templates.GetTemplate(api, project, store.Analyze, anonymizeAPIRequest.AnalyzeTemplateId, anonymizeAPIRequest.AnalyzeTemplate)
	if err != nil {
		return nil, err
	}

	err = templates.GetTemplate(api, project, store.Anonymize, anonymizeAPIRequest.AnonymizeTemplateId, anonymizeAPIRequest.AnonymizeTemplate)
	if err != nil {
		return nil, err
	}

	analyzeRes, err := api.Services.AnalyzeItem(ctx, anonymizeAPIRequest.Text, anonymizeAPIRequest.AnalyzeTemplate)
	if err != nil {
		return nil, err
	}
	if analyzeRes == nil {
		return nil, fmt.Errorf("No analyze results")
	}

	anonymizeRes, err := api.Services.AnonymizeItem(ctx, analyzeRes.AnalyzeResults, anonymizeAPIRequest.Text, anonymizeAPIRequest.AnonymizeTemplate)
	if err != nil {
		return nil, err
	} else if anonymizeRes == nil {
		return nil, fmt.Errorf("No anonymize results")
	}
	return anonymizeRes, nil
}

func validateTemplate(anonymizeAPIRequest *types.AnonymizeApiRequest) error {
	if anonymizeAPIRequest.AnalyzeTemplateId == "" && anonymizeAPIRequest.AnalyzeTemplate == nil {
		return fmt.Errorf("Analyze template is missing or empty")
	} else if anonymizeAPIRequest.AnalyzeTemplate == nil {
		anonymizeAPIRequest.AnalyzeTemplate = &types.AnalyzeTemplate{}
	}

	if anonymizeAPIRequest.AnonymizeTemplateId == "" && anonymizeAPIRequest.AnonymizeTemplate == nil {
		return fmt.Errorf("Anonymize template is missing or empty")
	} else if anonymizeAPIRequest.AnonymizeTemplate == nil {
		anonymizeAPIRequest.AnonymizeTemplate = &types.AnonymizeTemplate{}
	}
	return nil
}
