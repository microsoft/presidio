package mocks

import (
	"context"
	"crypto/md5"

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

//RecognizersStoreMockedObject recognizers store mock
type RecognizersStoreMockedObject struct {
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

//GetAnalyzerMockEmptyResult get analyzer mock empty response
func GetAnalyzerMockEmptyResult() *types.AnalyzeResponse {
	return &types.AnalyzeResponse{
		AnalyzeResults: nil,
	}
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
		RequestId:      "21020352-c0bd-4af6-81e0-f1d53f34f2cb",
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

//GetRecognizersStoreGetMockResult get recognizers mock response
func GetRecognizersStoreGetMockResult() *types.RecognizersGetResponse {

	pattern := &types.Pattern{
		Name:  "FirstPattern",
		Regex: "myregex",
		Score: 0.1}
	patternArr := []*types.Pattern{}
	patternArr = append(patternArr, pattern)

	recognizer := &types.PatternRecognizer{
		Name:     "MockRecognizer",
		Entity:   "SPACESHIP",
		Language: "he",
		Patterns: patternArr,
	}

	recognizersArr := []*types.PatternRecognizer{}
	recognizersArr = append(recognizersArr, recognizer)

	return &types.RecognizersGetResponse{
		Recognizers: recognizersArr,
	}
}

//GetRecognizersStoreGetAllMockResult get recognizers mock response
func GetRecognizersStoreGetAllMockResult() *types.RecognizersGetResponse {

	pattern := &types.Pattern{
		Name:  "FirstPattern",
		Regex: "myregex",
		Score: 0.1}
	patternArr := []*types.Pattern{}
	patternArr = append(patternArr, pattern)

	recognizer := &types.PatternRecognizer{
		Name:     "MockRecognizer",
		Entity:   "SPACESHIP",
		Language: "he",
		Patterns: patternArr,
	}

	recognizer2 := &types.PatternRecognizer{
		Name:     "MockRecognizer2",
		Entity:   "SPACESHIP",
		Language: "he",
		Patterns: patternArr,
	}

	recognizersArr := []*types.PatternRecognizer{}
	recognizersArr = append(recognizersArr, recognizer)
	recognizersArr = append(recognizersArr, recognizer2)

	return &types.RecognizersGetResponse{
		Recognizers: recognizersArr,
	}
}

//GetRecognizersStoreInsertOrUpdateMockResult get recognizers mock response
func GetRecognizersStoreInsertOrUpdateMockResult() *types.RecognizersStoreResponse {
	return &types.RecognizersStoreResponse{}
}

//GetRecognizersStoreDeleteMockResult get recognizers mock response
func GetRecognizersStoreDeleteMockResult() *types.RecognizersStoreResponse {
	return &types.RecognizersStoreResponse{}
}

//GetRecognizersStoreGetHashMockResult get recognizers mock response
func GetRecognizersStoreGetHashMockResult() *types.RecognizerHashResponse {
	h := md5.New()
	bytesHash := h.Sum([]byte("recognizers objects will be here..."))
	return &types.RecognizerHashResponse{RecognizersHash: string(bytesHash)}
}

//GetRecognizersStoreServiceMock get service mock
func GetRecognizersStoreServiceMock(
	expectedGetResult *types.RecognizersGetResponse,
	expectedGetAllResult *types.RecognizersGetResponse,
	expectedInsertOrUpdateAllResult *types.RecognizersStoreResponse,
	expectedDeleteResult *types.RecognizersStoreResponse,
	expectedHashResult *types.RecognizerHashResponse) types.RecognizersStoreServiceClient {
	service := &RecognizersStoreMockedObject{}
	service.On("ApplyGet", mock.Anything, mock.Anything, mock.Anything).Return(expectedGetResult, nil)
	service.On("ApplyGetAll", mock.Anything, mock.Anything, mock.Anything).Return(expectedGetAllResult, nil)
	service.On("ApplyInsert", mock.Anything, mock.Anything, mock.Anything).Return(expectedInsertOrUpdateAllResult, nil)
	service.On("ApplyUpdate", mock.Anything, mock.Anything, mock.Anything).Return(expectedInsertOrUpdateAllResult, nil)
	service.On("ApplyDelete", mock.Anything, mock.Anything, mock.Anything).Return(expectedDeleteResult, nil)
	service.On("ApplyGetHash", mock.Anything, mock.Anything, mock.Anything).Return(expectedHashResult, nil)
	return service
}

//ApplyGet recognizers mock
func (m *RecognizersStoreMockedObject) ApplyGet(ctx context.Context, r *types.RecognizerGetRequest, opts ...grpc.CallOption) (*types.RecognizersGetResponse, error) {
	args := m.Mock.Called()
	var result *types.RecognizersGetResponse
	if args.Get(0) != nil {
		result = args.Get(0).(*types.RecognizersGetResponse)
	}
	return result, args.Error(1)
}

//ApplyGetAll recognizers mock
func (m *RecognizersStoreMockedObject) ApplyGetAll(ctx context.Context, r *types.RecognizersGetAllRequest, opts ...grpc.CallOption) (*types.RecognizersGetResponse, error) {
	args := m.Mock.Called()
	var result *types.RecognizersGetResponse
	if args.Get(0) != nil {
		result = args.Get(0).(*types.RecognizersGetResponse)
	}
	return result, args.Error(1)
}

//ApplyInsert recognizers mock
func (m *RecognizersStoreMockedObject) ApplyInsert(ctx context.Context, r *types.RecognizerInsertOrUpdateRequest, opts ...grpc.CallOption) (*types.RecognizersStoreResponse, error) {
	args := m.Mock.Called()
	var result *types.RecognizersStoreResponse
	if args.Get(0) != nil {
		result = args.Get(0).(*types.RecognizersStoreResponse)
	}
	return result, args.Error(1)
}

//ApplyUpdate recognizers mock
func (m *RecognizersStoreMockedObject) ApplyUpdate(ctx context.Context, r *types.RecognizerInsertOrUpdateRequest, opts ...grpc.CallOption) (*types.RecognizersStoreResponse, error) {
	args := m.Mock.Called()
	var result *types.RecognizersStoreResponse
	if args.Get(0) != nil {
		result = args.Get(0).(*types.RecognizersStoreResponse)
	}
	return result, args.Error(1)
}

//ApplyDelete recognizers mock
func (m *RecognizersStoreMockedObject) ApplyDelete(ctx context.Context, r *types.RecognizerDeleteRequest, opts ...grpc.CallOption) (*types.RecognizersStoreResponse, error) {
	args := m.Mock.Called()
	var result *types.RecognizersStoreResponse
	if args.Get(0) != nil {
		result = args.Get(0).(*types.RecognizersStoreResponse)
	}
	return result, args.Error(1)
}

//ApplyGetHash recognizers mock
func (m *RecognizersStoreMockedObject) ApplyGetHash(ctx context.Context, r *types.RecognizerGetHashRequest, opts ...grpc.CallOption) (*types.RecognizerHashResponse, error) {
	args := m.Mock.Called()
	var result *types.RecognizerHashResponse
	if args.Get(0) != nil {
		result = args.Get(0).(*types.RecognizerHashResponse)
	}
	return result, args.Error(1)
}
