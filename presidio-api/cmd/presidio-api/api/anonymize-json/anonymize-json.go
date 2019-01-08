package anonymizejson

import (
	"context"
	"fmt"

	types "github.com/Microsoft/presidio-genproto/golang"
	store "github.com/Microsoft/presidio/presidio-api/cmd/presidio-api/api"
	"github.com/Microsoft/presidio/presidio-api/cmd/presidio-api/api/templates"
)

//AnonymizeJSON anonymizes structred json
func AnonymizeJSON(ctx context.Context, api *store.API, anonymizeJSONApiRequest *types.AnonymizeJsonApiRequest, project string) (*types.AnonymizeResponse, error) {

	err := validateTemplate(anonymizeJSONApiRequest)
	if err != nil {
		return nil, err
	}

	err = templates.GetTemplate(api, project, store.Analyze, anonymizeJSONApiRequest.AnalyzeTemplateId, anonymizeJSONApiRequest.AnalyzeTemplate)
	if err != nil {
		return nil, err
	}

	err = templates.GetTemplate(api, project, store.Anonymize, anonymizeJSONApiRequest.AnonymizeTemplateId, anonymizeJSONApiRequest.AnonymizeTemplate)
	if err != nil {
		return nil, err
	}

	err = templates.GetTemplate(api, project, store.AnonymizeJSON, anonymizeJSONApiRequest.JsonSchemaId, anonymizeJSONApiRequest.JsonSchemaTemplate)
	if err != nil {
		return nil, err
	}

	anonymizeResult, err := api.Services.AnonymizeJSON(ctx, anonymizeJSONApiRequest.Json, anonymizeJSONApiRequest.JsonSchemaTemplate.GetJsonSchema(), anonymizeJSONApiRequest.AnalyzeTemplate, anonymizeJSONApiRequest.AnonymizeTemplate)
	if err != nil {
		return nil, err
	} else if anonymizeResult == nil {
		return nil, fmt.Errorf("No anonymize results")
	}
	return anonymizeResult, nil
}

func validateTemplate(anonymizeJSONApiRequest *types.AnonymizeJsonApiRequest) error {
	if anonymizeJSONApiRequest.AnalyzeTemplateId == "" && anonymizeJSONApiRequest.AnalyzeTemplate == nil {
		return fmt.Errorf("Analyze template is missing or empty")
	} else if anonymizeJSONApiRequest.AnalyzeTemplate == nil {
		anonymizeJSONApiRequest.AnalyzeTemplate = &types.AnalyzeTemplate{}
	}

	if anonymizeJSONApiRequest.AnonymizeTemplateId == "" && anonymizeJSONApiRequest.AnonymizeTemplate == nil {
		return fmt.Errorf("Anonymize template is missing or empty")
	} else if anonymizeJSONApiRequest.AnonymizeTemplate == nil {
		anonymizeJSONApiRequest.AnonymizeTemplate = &types.AnonymizeTemplate{}
	}

	if anonymizeJSONApiRequest.JsonSchemaId == "" && anonymizeJSONApiRequest.JsonSchemaTemplate == nil {
		return fmt.Errorf("JsonSchema template is missing or empty")
	} else if anonymizeJSONApiRequest.JsonSchemaTemplate == nil {
		anonymizeJSONApiRequest.JsonSchemaTemplate = &types.JsonSchemaTemplate{}
	}
	return nil
}
