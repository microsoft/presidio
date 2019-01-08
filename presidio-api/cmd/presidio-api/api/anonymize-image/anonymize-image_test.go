package anonymizeimage

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
		AnalyzerService:       mocks.GetAnalyzeServiceMock(mocks.GetAnalyzerMockResult()),
		AnonymizeImageService: mocks.GetAnonymizerImageServiceMock(mocks.GetAnonymizerImageMockResult()),
		OcrService:            mocks.GetOcrServiceMock(mocks.GetOcrMockResult()),
	}

	api := &store.API{
		Services:  srv,
		Templates: mocks.GetTemplateMock(),
	}
	return api
}

func TestAnonymizeImageWithTemplateId(t *testing.T) {

	api := setupMockServices()

	project := "tests"
	anonymizeImageAPIRequest := &types.AnonymizeImageApiRequest{
		AnalyzeTemplateId:        "test",
		AnalyzeTemplate:          &types.AnalyzeTemplate{},
		AnonymizeImageTemplateId: "test",
		ImageType:                "image/jpg",
		Data:                     make([]byte, 1),
	}

	results, err := AnonymizeImage(context.Background(), api, anonymizeImageAPIRequest, project)

	assert.NoError(t, err)
	assert.True(t, len(results) > 0)
}

func TestAnonymizeImageWithTemplateStruct(t *testing.T) {

	api := setupMockServices()

	project := "tests"
	anonymizeImageAPIRequest := &types.AnonymizeImageApiRequest{
		AnalyzeTemplateId: "test",
		ImageType:         "image/jpg",
		AnalyzeTemplate:   &types.AnalyzeTemplate{},
		AnonymizeImageTemplate: &types.AnonymizeImageTemplate{
			FieldTypeGraphics: []*types.FieldTypeGraphic{{
				Graphic: &types.Graphic{
					FillColorValue: &types.FillColorValue{
						Blue:  50,
						Red:   50,
						Green: 50,
					},
				},
			}},
		},
		Data: make([]byte, 1),
	}

	results, err := AnonymizeImage(context.Background(), api, anonymizeImageAPIRequest, project)

	assert.NoError(t, err)
	assert.True(t, len(results) > 0)
}

func TestAnonymizeImageWithNoTemplate(t *testing.T) {

	api := setupMockServices()

	project := "tests"
	anonymizeImageAPIRequest := &types.AnonymizeImageApiRequest{
		AnalyzeTemplateId: "test",
		Data:              make([]byte, 1),
	}

	_, err := AnonymizeImage(context.Background(), api, anonymizeImageAPIRequest, project)

	assert.Error(t, err)
}
