package anonymize

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
		AnalyzerService:  mocks.GetAnalyzeServiceMock(mocks.GetAnalyzerMockResult()),
		AnonymizeService: mocks.GetAnonymizerServiceMock(mocks.GetAnonymizerMockResult()),
	}

	api := &store.API{
		Services:  srv,
		Templates: mocks.GetTemplateMock(),
	}
	return api
}

func TestAnonymizeWithTemplateId(t *testing.T) {

	api := setupMockServices()

	project := "tests"
	anonymizeAPIRequest := &types.AnonymizeApiRequest{
		Text:                "My number is (555) 253-0000 and email johnsnow@foo.com",
		AnalyzeTemplateId:   "test",
		AnalyzeTemplate:     &types.AnalyzeTemplate{},
		AnonymizeTemplateId: "test",
	}

	results, err := Anonymize(context.Background(), api, anonymizeAPIRequest, project)

	assert.NoError(t, err)
	assert.Equal(t, "My number is <phone> and email <email>", results.Text)
}

func TestAnonymizeWithTemplateStruct(t *testing.T) {

	api := setupMockServices()

	project := "tests"
	anonymizeAPIRequest := &types.AnonymizeApiRequest{
		Text:              "My number is (555) 253-0000 and email johnsnow@foo.com",
		AnalyzeTemplateId: "test",
		AnalyzeTemplate:   &types.AnalyzeTemplate{},
		AnonymizeTemplate: &types.AnonymizeTemplate{
			FieldTypeTransformations: []*types.FieldTypeTransformation{{
				Fields: []*types.FieldTypes{{
					Name: types.FieldTypesEnum_PHONE_NUMBER.String(),
				}},
				Transformation: &types.Transformation{
					ReplaceValue: &types.ReplaceValue{
						NewValue: "<phone>",
					},
				},
			}, {
				Fields: []*types.FieldTypes{{
					Name: types.FieldTypesEnum_EMAIL_ADDRESS.String(),
				}},
				Transformation: &types.Transformation{
					ReplaceValue: &types.ReplaceValue{
						NewValue: "<email>",
					},
				},
			}},
		},
	}

	results, err := Anonymize(context.Background(), api, anonymizeAPIRequest, project)

	assert.NoError(t, err)
	assert.Equal(t, "My number is <phone> and email <email>", results.Text)
}

func TestAnonymizeWithNoTemplate(t *testing.T) {

	api := setupMockServices()

	project := "tests"
	anonymizeAPIRequest := &types.AnonymizeApiRequest{
		Text:              "My number is (555) 253-0000 and email johnsnow@foo.com",
		AnalyzeTemplateId: "test",
	}

	_, err := Anonymize(context.Background(), api, anonymizeAPIRequest, project)

	assert.Error(t, err)
}
