package main

import (
	"context"
	"errors"

	"github.com/stretchr/testify/assert"

	"strings"
	"testing"

	"github.com/presid-io/stow"
	"github.com/stretchr/testify/mock"
	"google.golang.org/grpc"

	message_types "github.com/Microsoft/presidio-genproto/golang"
	c "github.com/Microsoft/presidio/pkg/cache"
	cache_mock "github.com/Microsoft/presidio/pkg/cache/mock"
	log "github.com/Microsoft/presidio/pkg/logger"
	"github.com/Microsoft/presidio/pkg/storage"
)

var (
	// Azure emulator connection string
	azureStorageName = "devstoreaccount1"
	azureStorageKey  = "Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw=="
	s3AccessID       = "foo"
	s3AccessKey      = "bar"
	s3Endpoint       = "http://localhost:9090"
	s3Region         = "us-east-1"
	testCache        c.Cache
)

// Mocks
type ScannerMockedObject struct {
	mock.Mock
}

type DataSyncMockedObject struct {
	mock.Mock
}

func (m *ScannerMockedObject) Apply(c context.Context, analyzeRequest *message_types.AnalyzeRequest, opts ...grpc.CallOption) (*message_types.AnalyzeResponse, error) {
	args := m.Mock.Called()
	var result *message_types.AnalyzeResponse
	if args.Get(0) != nil {
		result = args.Get(0).(*message_types.AnalyzeResponse)
	}
	return result, args.Error(1)
}

func (m *DataSyncMockedObject) Init(ctx context.Context, dataSyncTemplate *message_types.DataSyncTemplate, opts ...grpc.CallOption) (*message_types.DataSyncResponse, error) {
	// Currently not in use.
	return nil, nil
}
func (m *DataSyncMockedObject) Completion(ctx context.Context, dataSyncTemplate *message_types.CompletionMessage, opts ...grpc.CallOption) (*message_types.DataSyncResponse, error) {
	// Currently not in use.
	return nil, nil
}

func (m *DataSyncMockedObject) Apply(ctx context.Context, in *message_types.DataSyncRequest, opts ...grpc.CallOption) (*message_types.DataSyncResponse, error) {
	args := m.Mock.Called()
	var result *message_types.DataSyncResponse
	if args.Get(0) != nil {
		result = args.Get(0).(*message_types.DataSyncResponse)
	}
	return result, args.Error(1)
}

type testItem struct {
	path    string
	content string
}

// TESTS
func TestS3Scan(t *testing.T) {
	// Test setup
	testCache = cache_mock.New()
	kind, config := storage.CreateS3Config(s3AccessID, s3AccessKey, s3Region, s3Endpoint)
	scanRequest := getScannerRequest(kind)
	filePath := "dir/file1.txt"
	container := InitContainer(kind, config)
	putItems([]testItem{{path: filePath}}, container)
	scanner := createScanner(scanRequest)
	analyzeRequest := &message_types.AnalyzeRequest{}

	analyzerServiceMock := getAnalyzeServiceMock(getAnalyzerMockResult())
	dataSyncServiceMock := getDataSyncMock(nil)

	// Act
	n, err := Scan(scanner, scanRequest, testCache, &analyzerServiceMock, analyzeRequest, nil, &dataSyncServiceMock)

	// Verify
	item := getItem(filePath, container)
	etag, _ := item.ETag()
	cacheValue, _ := testCache.Get(etag)

	assert.Nil(t, err)
	assert.Equal(t, "test/"+filePath, cacheValue)
	assert.Equal(t, n, 1)

	// On the second scan the item that was already scan should'nt be scanned again
	n, err = Scan(scanner, scanRequest, testCache, &analyzerServiceMock, analyzeRequest, nil, &dataSyncServiceMock)
	assert.Nil(t, err)
	assert.Equal(t, n, 0)
}

func TestAzureScan(t *testing.T) {
	// Test setup
	testCache = cache_mock.New()
	kind, config := storage.CreateAzureConfig(azureStorageName, azureStorageKey)
	scanRequest := &message_types.ScanRequest{
		Kind: kind,
	}
	filePath := "dir/file1.txt"
	container := InitContainer(kind, config)
	putItems([]testItem{{path: filePath}}, container)
	scanner := createScanner(getScannerRequest(kind))
	analyzeRequest := &message_types.AnalyzeRequest{}

	analyzerServiceMock := getAnalyzeServiceMock(getAnalyzerMockResult())
	dataSyncServiceMock := getDataSyncMock(nil)

	// Act
	n, err := Scan(scanner, scanRequest, testCache, &analyzerServiceMock, analyzeRequest, nil, &dataSyncServiceMock)

	// Verify
	item := getItem(filePath, container)
	etag, _ := item.ETag()
	cacheValue, _ := testCache.Get(etag)

	assert.Nil(t, err)
	assert.Equal(t, "/devstoreaccount1/test/"+filePath, cacheValue)
	assert.Equal(t, n, 1)

	// On the second scan the item that was already scan should'nt be scanned again
	n, err = Scan(scanner, scanRequest, testCache, &analyzerServiceMock, analyzeRequest, nil, &dataSyncServiceMock)
	assert.Nil(t, err)
	assert.Equal(t, n, 0)
}

func TestFileExtension(t *testing.T) {
	testCache = cache_mock.New()
	kind, config := storage.CreateAzureConfig(azureStorageName, azureStorageKey)

	filePath := "dir/file1.jpg"
	container := InitContainer(kind, config)
	putItems([]testItem{{path: filePath}}, container)
	scanner := createScanner(getScannerRequest(kind))
	analyzeRequest := &message_types.AnalyzeRequest{}
	scanRequest := &message_types.ScanRequest{
		Kind: "azureblob",
	}

	analyzerServiceMock := getAnalyzeServiceMock(getAnalyzerMockResult())
	dataSyncServiceMock := getDataSyncMock(nil)

	// Act
	_, err := Scan(scanner, scanRequest, testCache, &analyzerServiceMock, analyzeRequest, nil, &dataSyncServiceMock)
	assert.Equal(t, err.Error(), "Expected: file extension txt, csv, json, tsv, received: .jpg")
}

func TestSendResultToDataSyncReturnsError(t *testing.T) {
	testCache = cache_mock.New()
	kind, config := storage.CreateAzureConfig(azureStorageName, azureStorageKey)
	scanRequest := &message_types.ScanRequest{
		Kind: "azureblob",
	}

	filePath := "dir/file1.txt"
	container := InitContainer(kind, config)
	putItems([]testItem{{path: filePath}}, container)
	scanner := createScanner(getScannerRequest(kind))
	analyzeRequest := &message_types.AnalyzeRequest{}
	analyzerServiceMock := getAnalyzeServiceMock(getAnalyzerMockResult())
	dataSyncServiceMock := getDataSyncMock(errors.New("some error"))

	// Act
	_, err := Scan(scanner, scanRequest, testCache, &analyzerServiceMock, analyzeRequest, nil, &dataSyncServiceMock)

	// Verify
	assert.EqualValues(t, err.Error(), "some error")
}

// TEST HELPERS
func getAnalyzeServiceMock(expectedResult *message_types.AnalyzeResponse) message_types.AnalyzeServiceClient {
	analyzeService := &ScannerMockedObject{}
	anlyzeServiceMock := analyzeService
	analyzeService.On("Apply", mock.Anything, mock.Anything, mock.Anything).Return(expectedResult, nil)
	return anlyzeServiceMock
}

func getDataSyncMock(expectedError error) message_types.DataSyncServiceClient {
	dataSyncSrv := &DataSyncMockedObject{}
	var dataSyncMock message_types.DataSyncServiceClient = dataSyncSrv
	dataSyncSrv.On("Apply", mock.Anything, mock.Anything, mock.Anything).Return(nil, expectedError)
	return dataSyncMock
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

func InitContainer(kind string, config stow.ConfigMap) stow.Container {
	api, _ := storage.New(kind, config, 10)
	api.RemoveContainer("test")
	return createContainer(api)
}

func getItem(name string, container stow.Container) stow.Item {
	item, _ := container.Item(name)
	return item
}

func createContainer(api *storage.API) stow.Container {
	container, err := api.CreateContainer("test")
	if err != nil {
		log.Fatal(err.Error())
	}
	return container
}

func putItems(items []testItem, container stow.Container) {
	for _, item := range items {
		if item.content == "" {
			item.content = "Please call me. My phone number is (555) 253-0000."
		}

		_, err := container.Put(item.path, strings.NewReader(item.content), int64(len(item.content)), nil)
		if err != nil {
			log.Fatal(err.Error())
		}
	}
}

func getScannerRequest(kind string) *message_types.ScanRequest {
	if kind == "azureblob" {
		return &message_types.ScanRequest{
			CloudStorageConfig: &message_types.CloudStorageConfig{
				BlobStorageConfig: &message_types.BlobStorageConfig{
					AccountName:   azureStorageName,
					AccountKey:    azureStorageKey,
					ContainerName: "test",
				},
			},
			Kind: "azureblob",
		}
	}
	return &message_types.ScanRequest{
		CloudStorageConfig: &message_types.CloudStorageConfig{
			S3Config: &message_types.S3Config{
				AccessId:   s3AccessID,
				AccessKey:  s3AccessKey,
				Endpoint:   s3Endpoint,
				Region:     s3Region,
				BucketName: "test",
			},
		},
		Kind: "s3",
	}
}
