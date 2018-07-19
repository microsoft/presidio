package main

import (
	"context"
	"errors"

	"strings"
	"testing"

	"github.com/presid-io/stow"
	"github.com/stretchr/testify/mock"
	"google.golang.org/grpc"

	"github.com/stretchr/testify/assert"

	message_types "github.com/presid-io/presidio-genproto/golang"
	c "github.com/presid-io/presidio/pkg/cache"
	cache_mock "github.com/presid-io/presidio/pkg/cache/mock"
	log "github.com/presid-io/presidio/pkg/logger"
	"github.com/presid-io/presidio/pkg/modules/analyzer"
	"github.com/presid-io/presidio/pkg/storage"
)

var (
	// Azure emulator connection string
	storageName = "devstoreaccount1"
	storageKey  = "Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw=="
	testCache   c.Cache
	serviceMock analyzer.Analyzer
)

// Mocks
type MyMockedObject struct {
	mock.Mock
}

func (m *MyMockedObject) InvokeAnalyze(c context.Context, analyzeRequest *message_types.AnalyzeRequest, text string) (*message_types.AnalyzeResponse, error) {
	args := m.Mock.Called()
	var result *message_types.AnalyzeResponse
	if args.Get(0) != nil {
		result = args.Get(0).(*message_types.AnalyzeResponse)
	}
	return result, args.Error(1)
}

func (m *MyMockedObject) Init(ctx context.Context, databinderTemplate *message_types.DatabinderTemplate, opts ...grpc.CallOption) (*message_types.DatabinderResponse, error) {
	// Currently not in use.
	return nil, nil
}

func (m *MyMockedObject) Apply(ctx context.Context, in *message_types.DatabinderRequest, opts ...grpc.CallOption) (*message_types.DatabinderResponse, error) {
	args := m.Mock.Called()
	var result *message_types.DatabinderResponse
	if args.Get(0) != nil {
		result = args.Get(0).(*message_types.DatabinderResponse)
	}
	return result, args.Error(1)
}

// TESTS
func TestAzureScanAndAnalyze(t *testing.T) {
	testCache = cache_mock.New()
	kind, config := storage.CreateAzureConfig(storageName, storageKey)

	analyzerObj := &MyMockedObject{}
	serviceMock = analyzerObj
	analyzerObj.On("InvokeAnalyze", mock.Anything, mock.Anything, mock.Anything).Return(getAnalyzerMockResult(), nil)

	api, _ := storage.New(kind, config, 10)
	api.RemoveContainer("test")
	container := createContainer(api)
	putItem("file1.txt", container, api)
	scannerObj = createScanner(getScannerTemplate())

	// Act
	api.WalkFiles(container, func(item stow.Item) {
		itemPath := scannerObj.GetItemPath(item)
		uniqueID, _ := scannerObj.GetItemUniqueID(item)
		results, _ := analyzeItem(&testCache, uniqueID, &serviceMock, nil, item)
		// validate output
		assert.Equal(t, len(results), 1)
		assert.Equal(t, results[0].GetField().Name, "PHONE_NUMBER")
		assert.Equal(t, results[0].Probability, float32(1))
		writeItemToCache(uniqueID, itemPath, testCache)
	})

	api.WalkFiles(container, func(item stow.Item) {
		uniqueID, _ := scannerObj.GetItemUniqueID(item)
		results, err := analyzeItem(&testCache, uniqueID, &serviceMock, analyzeRequest, item)
		// validate output
		assert.Equal(t, len(results), 0)
		assert.Equal(t, err, nil)
	})

	// test cleanup
	api.RemoveContainer("test")
}

func TestFileExtension(t *testing.T) {
	// Setup
	testCache = cache_mock.New()
	kind, config := storage.CreateAzureConfig(storageName, storageKey)

	analyzerObj := &MyMockedObject{}
	serviceMock = analyzerObj

	api, _ := storage.New(kind, config, 10)
	container := createContainer(api)
	putItem("file1.jpg", container, api)
	scannerObj = createScanner(getScannerTemplate())
	// Assert
	api.WalkFiles(container, func(item stow.Item) {
		uniqueID, _ := scannerObj.GetItemUniqueID(item)
		results, err := analyzeItem(&testCache, uniqueID, &serviceMock, analyzeRequest, item)
		// validate output
		assert.Equal(t, len(results), 0)
		assert.Equal(t, err.Error(), "Expected: file extension txt, csv, json, tsv, received: .jpg")
	})

	// test cleanup
	api.RemoveContainer("test")
}

func TestSendResultToDataBinderReturnsErrorOnError(t *testing.T) {
	// Setup
	testCache = cache_mock.New()
	kind, config := storage.CreateAzureConfig(storageName, storageKey)
	api, _ := storage.New(kind, config, 10)

	container := createContainer(api)
	item := putItem("file1.jpg", container, api)
	itemPath := scannerObj.GetItemPath(item)
	dataBinderSrv := &MyMockedObject{}
	var databinderMock message_types.DatabinderServiceClient = dataBinderSrv
	dataBinderSrv.On("Apply", mock.Anything, mock.Anything, mock.Anything).Return(nil, errors.New("some error"))

	// Act
	err := sendResultToDataBinder(itemPath, getAnalyzerMockResult().AnalyzeResults, testCache, &databinderMock)

	// Assert
	assert.EqualValues(t, err.Error(), "some error")
}

func getAnalyzerMockResult() *message_types.AnalyzeResponse {
	location := &message_types.Location{
		Start: 153, End: 163, Length: 10,
	}
	results := [](*message_types.AnalyzeResult){
		&message_types.AnalyzeResult{
			Field:       &message_types.FieldTypes{Name: message_types.FieldTypesEnum_PHONE_NUMBER.String()},
			Text:        "(555) 253-0000",
			Probability: 1.0,
			Location:    location,
		},
	}
	response := &message_types.AnalyzeResponse{
		AnalyzeResults: results,
	}
	return response
}

func createContainer(api *storage.API) stow.Container {
	container, err := api.CreateContainer("test")
	if err != nil {
		log.Fatal(err.Error())
	}
	return container
}

func putItem(itemName string, container stow.Container, api *storage.API) stow.Item {
	content := "Please call me. My phone number is (555) 253-0000."

	item, err := container.Put(itemName, strings.NewReader(content), int64(len(content)), nil)
	if err != nil {
		log.Fatal(err.Error())
	}
	return item
}

func getScannerTemplate() *message_types.ScannerTemplate {
	scannerTemplate := &message_types.ScannerTemplate{
		InputConfig: &message_types.InputConfig{
			BlobStorageConfig: &message_types.BlobStorageConfig{
				AccountName:   storageName,
				AccountKey:    storageKey,
				ContainerName: "test",
			},
		},
		Kind: "azure",
	}
	return scannerTemplate
}
