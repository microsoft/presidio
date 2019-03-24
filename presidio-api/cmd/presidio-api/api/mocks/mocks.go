package mocks

import (
	"context"

	types "github.com/Microsoft/presidio-genproto/golang"
	"github.com/Microsoft/presidio/pkg/presidio"
	store "github.com/Microsoft/presidio/presidio-api/cmd/presidio-api/api"

	"github.com/stretchr/testify/mock"
	"google.golang.org/grpc"
)

//AnalyzerMockedObject analyzer mock
type AnalyzerMockedObject struct {
	mock.Mock
}

//AnonymizerMockedObject anonymizer mock
type AnonymizerMockedObject struct {
	mock.Mock
}

//AnonymizerImageMockedObject anonymizer mock
type AnonymizerImageMockedObject struct {
	mock.Mock
}

//OcrMockedObject anonymizer mock
type OcrMockedObject struct {
	mock.Mock
}

//TemplateMockedObject template mock
type TemplateMockedObject struct {
	mock.Mock
}

//GetAnalyzerMockResult get analyzer mock response
func GetAnalyzerMockResult() *types.AnalyzeResponse {
	location := &types.Location{
		Start: 153, End: 163, Length: 10,
	}
	results := [](*types.AnalyzeResult){
		&types.AnalyzeResult{
			Field:    &types.FieldTypes{Name: types.FieldTypesEnum_PHONE_NUMBER.String()},
			Text:     "(555) 253-0000",
			Score:    1.0,
			Location: location,
		},
		&types.AnalyzeResult{
			Field:    &types.FieldTypes{Name: types.FieldTypesEnum_EMAIL_ADDRESS.String()},
			Text:     "johnsnow@foo.com",
			Score:    1.0,
			Location: location,
		},
	}
	return &types.AnalyzeResponse{
		AnalyzeResults: results,
	}
}

//GetAnalyzeServiceMock get service mock
func GetAnalyzeServiceMock(expectedResult *types.AnalyzeResponse) types.AnalyzeServiceClient {
	analyzeService := &AnalyzerMockedObject{}
	analyzeService.On("Apply", mock.Anything, mock.Anything, mock.Anything).Return(expectedResult, nil)
	return analyzeService
}

//Apply analyzer mock
func (m *AnalyzerMockedObject) Apply(c context.Context, analyzeRequest *types.AnalyzeRequest, opts ...grpc.CallOption) (*types.AnalyzeResponse, error) {
	args := m.Mock.Called()
	var result *types.AnalyzeResponse
	if args.Get(0) != nil {
		result = args.Get(0).(*types.AnalyzeResponse)
	}
	return result, args.Error(1)
}

//GetAnonymizerMockResult get anonymizer mock response
func GetAnonymizerMockResult() *types.AnonymizeResponse {

	return &types.AnonymizeResponse{
		Text: "My number is <phone> and email <email>",
	}
}

//GetAnonymizerServiceMock get service mock
func GetAnonymizerServiceMock(expectedResult *types.AnonymizeResponse) types.AnonymizeServiceClient {
	anonymizerService := &AnonymizerMockedObject{}
	anonymizerService.On("Apply", mock.Anything, mock.Anything, mock.Anything).Return(expectedResult, nil)
	return anonymizerService
}

//Apply anonymizer mock
func (m *AnonymizerMockedObject) Apply(c context.Context, anonymizeRequest *types.AnonymizeRequest, opts ...grpc.CallOption) (*types.AnonymizeResponse, error) {
	args := m.Mock.Called()
	var result *types.AnonymizeResponse
	if args.Get(0) != nil {
		result = args.Get(0).(*types.AnonymizeResponse)
	}
	return result, args.Error(1)
}

//GetAnonymizerImageServiceMock get service mock
func GetAnonymizerImageServiceMock(expectedResult *types.AnonymizeImageResponse) types.AnonymizeImageServiceClient {
	anonymizerImageService := &AnonymizerImageMockedObject{}
	anonymizerImageService.On("Apply", mock.Anything, mock.Anything, mock.Anything).Return(expectedResult, nil)
	return anonymizerImageService
}

//Apply anonymizer mock
func (m *AnonymizerImageMockedObject) Apply(c context.Context, anonymizeImageRequest *types.AnonymizeImageRequest, opts ...grpc.CallOption) (*types.AnonymizeImageResponse, error) {
	args := m.Mock.Called()
	var result *types.AnonymizeImageResponse
	if args.Get(0) != nil {
		result = args.Get(0).(*types.AnonymizeImageResponse)
	}
	return result, args.Error(1)
}

//GetAnonymizerImageMockResult get anonymizer image mock response
func GetAnonymizerImageMockResult() *types.AnonymizeImageResponse {

	return &types.AnonymizeImageResponse{
		Image: &types.Image{
			Data:          make([]byte, 1),
			Boundingboxes: make([]*types.Boundingbox, 1),
		},
	}
}

//GetOcrServiceMock get service mock
func GetOcrServiceMock(expectedResult *types.OcrResponse) types.OcrServiceClient {
	ocrService := &OcrMockedObject{}
	ocrService.On("Apply", mock.Anything, mock.Anything, mock.Anything).Return(expectedResult, nil)
	return ocrService
}

//Apply ocr mock
func (m *OcrMockedObject) Apply(c context.Context, ocrRequest *types.OcrRequest, opts ...grpc.CallOption) (*types.OcrResponse, error) {
	args := m.Mock.Called()
	var result *types.OcrResponse
	if args.Get(0) != nil {
		result = args.Get(0).(*types.OcrResponse)
	}
	return result, args.Error(1)
}

//GetOcrMockResult get ocr mock response
func GetOcrMockResult() *types.OcrResponse {

	return &types.OcrResponse{
		Image: &types.Image{
			Text: "My number is (555) 253-0000 and email johnsnow@foo.com",
		},
	}
}

//GetTemplateMock mock
func GetTemplateMock() presidio.TemplatesStore {
	templateService := &TemplateMockedObject{}
	templateService.On("GetTemplate", mock.Anything, store.Analyze, mock.Anything).
		Return(`{"fields":[{"name":"PHONE_NUMBER"}, {"name":"EMAIL_ADDRESS"}],"language":"langtest"}`, nil).
		On("GetTemplate", mock.Anything, store.Anonymize, mock.Anything).
		Return(`{"fieldTypeTransformations":[{"fields":[],"transformation":{"replaceValue":{"newValue":"<phone>"}}}]}`, nil).
		On("GetTemplate", mock.Anything, store.AnonymizeImage, mock.Anything).
		Return(`{"fieldTypeGraphics":[{"graphic":{"fillColorValue":{"blue":0,"red":0,"green":0}}}]}`, nil)
	return templateService
}

//GetTemplate mock
func (m *TemplateMockedObject) GetTemplate(project string, action string, id string) (string, error) {
	args := m.Mock.Called(project, action, id)
	result := args.String(0)
	return result, args.Error(1)
}

//InsertTemplate mock
func (m *TemplateMockedObject) InsertTemplate(project, action, id, value string) error {
	args := m.Mock.Called()
	return args.Error(1)
}

//UpdateTemplate mock
func (m *TemplateMockedObject) UpdateTemplate(project, action, id, value string) error {
	args := m.Mock.Called()
	return args.Error(1)
}

//DeleteTemplate mock
func (m *TemplateMockedObject) DeleteTemplate(project string, action string, id string) error {
	args := m.Mock.Called()
	return args.Error(1)
}
