package anonymizejson

import (
	"context"

	"github.com/stretchr/testify/assert"

	types "github.com/Microsoft/presidio-genproto/golang"
	"github.com/Microsoft/presidio/pkg/presidio/services"

	store "github.com/Microsoft/presidio/presidio-api/cmd/presidio-api/api"
	"github.com/Microsoft/presidio/presidio-api/cmd/presidio-api/api/mocks"

	"testing"
)

func setupMockServices() *store.API {
	srv := &services.Services{
		AnonymizeService: mocks.GetAnonymizerServiceMock(mocks.GetJSONAnonymizerMockResult()),
	}

	api := &store.API{
		Services:  srv,
		Templates: mocks.GetTemplateMock(),
	}
	return api
}

func TestAnonymizeJsonWithTemplateId(t *testing.T) {

	api := setupMockServices()

	project := "tests"
	anonymizeJSONAPIRequest := &types.AnonymizeJsonApiRequest{
		Json:                `{"Name":"John Davidson"}`,
		AnalyzeTemplateId:   "test",
		AnalyzeTemplate:     &types.AnalyzeTemplate{},
		AnonymizeTemplateId: "test",
		JsonSchemaId:        "test",
	}

	results, err := AnonymizeJSON(context.Background(), api, anonymizeJSONAPIRequest, project)

	assert.NoError(t, err)
	assert.Equal(t, `{"Name":"\u003cPERSON\u003e"}`, results.Text)
}

func TestAnonymizeJSONWithTemplateStruct(t *testing.T) {

	api := setupMockServices()

	project := "tests"
	anonymizeJSONAPIRequest := &types.AnonymizeJsonApiRequest{
		Json:                `{"Name":"John Davidson"}`,
		AnalyzeTemplateId:   "test",
		AnonymizeTemplateId: "test",
		AnalyzeTemplate:     &types.AnalyzeTemplate{},
		JsonSchemaTemplate: &types.JsonSchemaTemplate{
			JsonSchema: `{"Name":"\u003cPERSON\u003e"}`,
		},
	}

	results, err := AnonymizeJSON(context.Background(), api, anonymizeJSONAPIRequest, project)

	assert.NoError(t, err)
	assert.Equal(t, `{"Name":"\u003cPERSON\u003e"}`, results.Text)
}

func TestAnonymizeJSONWithNoTemplate(t *testing.T) {

	api := setupMockServices()

	project := "tests"
	anonymizeJSONAPIRequest := &types.AnonymizeJsonApiRequest{
		Json:                `{"Name":"John Davidson"}`,
		AnalyzeTemplateId:   "test",
		AnonymizeTemplateId: "test",
	}

	_, err := AnonymizeJSON(context.Background(), api, anonymizeJSONAPIRequest, project)

	assert.Error(t, err)
}
