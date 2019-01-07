package mocks

import (
	"context"

	types "github.com/Microsoft/presidio-genproto/golang"
	"github.com/Microsoft/presidio/pkg/presidio"

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

//GetAnonymizerMockResult get analyzer mock response
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

//GetTemplate mock
func (m *TemplateMockedObject) GetTemplate(project string, action string, id string) (string, error) {
	args := m.Mock.Called()
	var result string
	if args.Get(0) != nil {
		result = args.Get(0).(string)
	}
	return result, args.Error(1)
}

//GetEmptyTemplateMockResult mock
func GetEmptyTemplateMockResult() string {
	return "{}"
}

//GetTemplateMock mock
func GetTemplateMock(expectedResult string) presidio.TemplatesStore {
	templateService := &TemplateMockedObject{}
	templateService.On("GetTemplate", mock.Anything, mock.Anything, mock.Anything).Return(expectedResult, nil)
	return templateService
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
