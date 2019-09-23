package analyze

import (
	"context"
	"testing"

	uuid "github.com/satori/go.uuid"
	"github.com/stretchr/testify/assert"

	types "github.com/Microsoft/presidio-genproto/golang"
	"github.com/Microsoft/presidio/pkg/presidio/services"
	store "github.com/Microsoft/presidio/presidio-api/cmd/presidio-api/api"
	"github.com/Microsoft/presidio/presidio-api/cmd/presidio-api/api/mocks"
)

func setupMockServices() *store.API {
	srv := &services.Services{
		AnalyzerService: mocks.GetAnalyzeServiceMock(mocks.GetAnalyzerMockResult()),
	}

	api := &store.API{
		Services:  srv,
		Templates: mocks.GetTemplateMock(),
	}
	return api
}

func setupEmptyResponseMockServices() *store.API {
	srv := &services.Services{
		AnalyzerService: mocks.GetAnalyzeServiceMock(mocks.GetAnalyzerMockEmptyResult()),
	}

	api := &store.API{
		Services:  srv,
		Templates: mocks.GetTemplateMock(),
	}
	return api
}

func TestAnalyzeWithTemplateId(t *testing.T) {

	api := setupMockServices()

	project := "tests"
	analyzeAPIRequest := &types.AnalyzeApiRequest{
		Text:              "My number is (555) 253-0000 and email johnsnow@foo.com",
		AnalyzeTemplateId: "test",
	}
	response, err := Analyze(context.Background(), api, analyzeAPIRequest, project)
	assert.NoError(t, err)
	assert.Equal(t, 2, len(response.AnalyzeResults))
}

func TestAnalyzeWithTemplateStruct(t *testing.T) {

	api := setupMockServices()

	project := "tests"
	analyzeAPIRequest := &types.AnalyzeApiRequest{
		Text: "My number is (555) 253-0000 and email johnsnow@foo.com",
		AnalyzeTemplate: &types.AnalyzeTemplate{
			Fields: []*types.FieldTypes{
				{
					Name: types.FieldTypesEnum_PHONE_NUMBER.String(),
				},
				{
					Name: types.FieldTypesEnum_EMAIL_ADDRESS.String(),
				},
			},
		},
	}
	response, err := Analyze(context.Background(), api, analyzeAPIRequest, project)
	assert.NoError(t, err)
	assert.Equal(t, 2, len(response.AnalyzeResults))
}

func TestAnalyzeWithNoTemplate(t *testing.T) {

	api := setupMockServices()

	project := "tests"
	analyzeAPIRequest := &types.AnalyzeApiRequest{
		Text: "My number is (555) 253-0000 and email johnsnow@foo.com",
	}
	_, err := Analyze(context.Background(), api, analyzeAPIRequest, project)
	assert.Error(t, err)

}

func TestLanguageCode(t *testing.T) {

	api := setupMockServices()

	project := "tests"
	analyzeAPIRequest := &types.AnalyzeApiRequest{
		Text:              "My number is (555) 253-0000 and email johnsnow@foo.com",
		AnalyzeTemplateId: "test",
	}
	Analyze(context.Background(), api, analyzeAPIRequest, project)
	assert.Equal(t, "langtest", analyzeAPIRequest.AnalyzeTemplate.Language)
}

func TestAllFields(t *testing.T) {

	api := setupMockServices()

	project := "tests"
	analyzeAPIRequest := &types.AnalyzeApiRequest{
		Text: "My number is (555) 253-0000 and email johnsnow@foo.com",
		AnalyzeTemplate: &types.AnalyzeTemplate{
			Language:  "en",
			AllFields: true},
	}
	response, err := Analyze(context.Background(), api, analyzeAPIRequest, project)
	assert.NoError(t, err)
	assert.Equal(t, 2, len(response.AnalyzeResults))
	assert.NotEqual(t, "", response.RequestId)
	_, err = uuid.FromString(response.RequestId)
	assert.NoError(t, err)
}

func TestAnalyzeWhenNoEntitiesFoundThenExpectEmptyResponse(t *testing.T) {

	api := setupEmptyResponseMockServices()

	project := "tests"
	noResultsanalyzeAPIRequest := &types.AnalyzeApiRequest{
		Text: "hello world",
		AnalyzeTemplate: &types.AnalyzeTemplate{
			Language:  "en",
			AllFields: true},
	}
	response, err := Analyze(context.Background(), api, noResultsanalyzeAPIRequest, project)
	assert.NoError(t, err)
	assert.Equal(t, 0, len(response.AnalyzeResults))
}

func TestSettingTemplateAndTemplateIdReturnsError(t *testing.T) {
	api := setupMockServices()

	project := "tests"
	analyzeAPIRequest := &types.AnalyzeApiRequest{
		Text: "My number is (555) 253-0000 and email johnsnow@foo.com",
		AnalyzeTemplate: &types.AnalyzeTemplate{
			Language:  "en",
			AllFields: true},
		AnalyzeTemplateId: "123",
	}
	_, err := Analyze(context.Background(), api, analyzeAPIRequest, project)
	assert.Error(t, err)
}
