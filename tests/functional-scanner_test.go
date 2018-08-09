// +build functional

package tests

import (
	"context"
	"errors"
	"strings"
	"testing"

	"github.com/presid-io/stow"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"google.golang.org/grpc"

	message_types "github.com/Microsoft/presidio-genproto/golang"
	c "github.com/Microsoft/presidio/pkg/cache"
	cache_mock "github.com/Microsoft/presidio/pkg/cache/mock"
	log "github.com/Microsoft/presidio/pkg/logger"
	"github.com/Microsoft/presidio/pkg/storage"
	"github.com/Microsoft/presidio/pkg/templates"
	"github.com/Microsoft/presidio/presidio-datasink/cmd/presidio-datasink/cloudstorage"
	s "github.com/Microsoft/presidio/presidio-scanner/cmd/presidio-scanner/scanner"
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

type DatasinkMockedObject struct {
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

func (m *DatasinkMockedObject) Init(ctx context.Context, datasinkTemplate *message_types.DatasinkTemplate, opts ...grpc.CallOption) (*message_types.DatasinkResponse, error) {
	// Currently not in use.
	return nil, nil
}
func (m *DatasinkMockedObject) Completion(ctx context.Context, datasinkTemplate *message_types.CompletionMessage, opts ...grpc.CallOption) (*message_types.DatasinkResponse, error) {
	// Currently not in use.
	return nil, nil
}

func (m *DatasinkMockedObject) Apply(ctx context.Context, in *message_types.DatasinkRequest, opts ...grpc.CallOption) (*message_types.DatasinkResponse, error) {
	args := m.Mock.Called()
	var result *message_types.DatasinkResponse
	if args.Get(0) != nil {
		result = args.Get(0).(*message_types.DatasinkResponse)
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
	scanner := s.CreateScanner(scanRequest)
	analyzeRequest := &message_types.AnalyzeRequest{}

	analyzerServiceMock := getAnalyzeServiceMock(getAnalyzerMockResult())
	datasinkServiceMock := getDatasinkMock(nil)

	// Act
	n, err := s.ScanData(scanner, scanRequest, testCache, &analyzerServiceMock, analyzeRequest, nil, &datasinkServiceMock)

	// Verify
	item := getItem(filePath, container)
	etag, _ := item.ETag()
	cacheValue, _ := testCache.Get(etag)

	assert.Nil(t, err)
	assert.Equal(t, "test/"+filePath, cacheValue)
	assert.Equal(t, n, 1)

	// On the second scan the item that was already scan should'nt be scanned again
	n, err = s.ScanData(scanner, scanRequest, testCache, &analyzerServiceMock, analyzeRequest, nil, &datasinkServiceMock)
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
	scanner := s.CreateScanner(getScannerRequest(kind))
	analyzeRequest := &message_types.AnalyzeRequest{}

	analyzerServiceMock := getAnalyzeServiceMock(getAnalyzerMockResult())
	datasinkServiceMock := getDatasinkMock(nil)

	// Act
	n, err := s.ScanData(scanner, scanRequest, testCache, &analyzerServiceMock, analyzeRequest, nil, &datasinkServiceMock)

	// Verify
	item := getItem(filePath, container)
	etag, _ := item.ETag()
	cacheValue, _ := testCache.Get(etag)

	assert.Nil(t, err)
	assert.Equal(t, "/devstoreaccount1/test/"+filePath, cacheValue)
	assert.Equal(t, n, 1)

	// On the second scan the item that was already scan should'nt be scanned again
	n, err = s.ScanData(scanner, scanRequest, testCache, &analyzerServiceMock, analyzeRequest, nil, &datasinkServiceMock)
	assert.Nil(t, err)
	assert.Equal(t, n, 0)
}

func TestFileExtension(t *testing.T) {
	testCache = cache_mock.New()
	kind, config := storage.CreateAzureConfig(azureStorageName, azureStorageKey)

	filePath := "dir/file1.jpg"
	container := InitContainer(kind, config)
	putItems([]testItem{{path: filePath}}, container)
	scanner := s.CreateScanner(getScannerRequest(kind))
	analyzeRequest := &message_types.AnalyzeRequest{}
	scanRequest := &message_types.ScanRequest{
		Kind: "azureblob",
	}

	analyzerServiceMock := getAnalyzeServiceMock(getAnalyzerMockResult())
	datasinkServiceMock := getDatasinkMock(nil)

	// Act
	_, err := s.ScanData(scanner, scanRequest, testCache, &analyzerServiceMock, analyzeRequest, nil, &datasinkServiceMock)
	assert.Equal(t, err.Error(), "Expected: file extension txt, csv, json, tsv, received: .jpg")
}

func TestSendResultToDatasinkReturnsError(t *testing.T) {
	testCache = cache_mock.New()
	kind, config := storage.CreateAzureConfig(azureStorageName, azureStorageKey)
	scanRequest := &message_types.ScanRequest{
		Kind: "azureblob",
	}

	filePath := "dir/file1.txt"
	container := InitContainer(kind, config)
	putItems([]testItem{{path: filePath}}, container)
	scanner := s.CreateScanner(getScannerRequest(kind))
	analyzeRequest := &message_types.AnalyzeRequest{}
	analyzerServiceMock := getAnalyzeServiceMock(getAnalyzerMockResult())
	datasinkServiceMock := getDatasinkMock(errors.New("some error"))

	// Act
	_, err := s.ScanData(scanner, scanRequest, testCache, &analyzerServiceMock, analyzeRequest, nil, &datasinkServiceMock)

	// Verify
	assert.EqualValues(t, err.Error(), "some error")
}

func TestResultWrittenToStorage(t *testing.T) {
	// Setup
	containerName := "cloudstoragetest"
	kind, config := storage.CreateAzureConfig(azureStorageName, azureStorageKey)
	api, _ := storage.New(kind, config, 10)
	api.RemoveContainer(containerName)

	datasink := &message_types.Datasink{
		CloudStorageConfig: &message_types.CloudStorageConfig{
			BlobStorageConfig: &message_types.BlobStorageConfig{
				AccountKey:    azureStorageKey,
				AccountName:   azureStorageName,
				ContainerName: containerName,
			},
		},
	}

	cloudStorage := cloudStorage.New(datasink, "azureblob")
	resultsPath := "someDir/SomeFile.txt"
	anonymizeResponse := &message_types.AnonymizeResponse{
		Text: "<Person> live is <Location>",
	}
	//Act
	cloudStorage.WriteAnalyzeResults(getAnalyzerMockResult().AnalyzeResults, resultsPath)
	cloudStorage.WriteAnonymizeResults(anonymizeResponse, resultsPath)

	//Verify
	container, _ := api.CreateContainer(containerName)
	count := 0

	api.WalkFiles(container, func(item stow.Item) {
		count++
		if strings.Contains(item.Name(), "analyzed") {
			analyzedFile, _ := storage.ReadObject(item)
			expectedContent, _ := templates.ConvertInterfaceToJSON(getAnalyzerMockResult().AnalyzeResults)
			assert.Equal(t, analyzedFile, expectedContent)
		} else if strings.Contains(item.Name(), "anonymized") {
			anonymizedFile, _ := storage.ReadObject(item)
			assert.Equal(t, anonymizedFile, anonymizeResponse.Text)
		}
	})

	assert.Equal(t, count, 2)

	// Cleanup
	api.RemoveContainer(containerName)
}

// TEST HELPERS
func getAnalyzeServiceMock(expectedResult *message_types.AnalyzeResponse) message_types.AnalyzeServiceClient {
	analyzeService := &ScannerMockedObject{}
	anlyzeServiceMock := analyzeService
	analyzeService.On("Apply", mock.Anything, mock.Anything, mock.Anything).Return(expectedResult, nil)
	return anlyzeServiceMock
}

func getDatasinkMock(expectedError error) message_types.DatasinkServiceClient {
	datasinkSrv := &DatasinkMockedObject{}
	var datasinkMock message_types.DatasinkServiceClient = datasinkSrv
	datasinkSrv.On("Apply", mock.Anything, mock.Anything, mock.Anything).Return(nil, expectedError)
	return datasinkMock
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
