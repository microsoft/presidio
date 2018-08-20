// +build functional

package tests

import (
	"context"
	"errors"
	"fmt"
	"strings"
	"testing"

	"github.com/presid-io/stow"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"go.uber.org/zap"
	"google.golang.org/grpc"

	message_types "github.com/Microsoft/presidio-genproto/golang"
	c "github.com/Microsoft/presidio/pkg/cache"
	cache_mock "github.com/Microsoft/presidio/pkg/cache/mock"
	log "github.com/Microsoft/presidio/pkg/logger"
	"github.com/Microsoft/presidio/pkg/storage"
	"github.com/Microsoft/presidio/pkg/templates"
	"github.com/Microsoft/presidio/presidio-datasink/cmd/presidio-datasink/cloudstorage"
	"github.com/Microsoft/presidio/presidio-scanner/cmd/presidio-scanner/scanner"
)

var (
	// Azure emulator connection string
	azureStorageName = "devstoreaccount1"
	azureStorageKey  = "Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw=="
	azureKind        = "azure"
	azureConfig      stow.ConfigMap
	s3Kind           = "s3"
	s3AccessID       = "foo"
	s3AccessKey      = "bar"
	s3Endpoint       = "http://localhost:9090"
	s3Region         = "us-east-1"
	s3Config         stow.ConfigMap
	containerName    = "test"
	testCache        c.Cache
	datasinkSrv      = &DatasinkMockedObject{}
)

func init() {
	log.ObserveLogging(zap.InfoLevel)
	s3Config = storage.CreateS3Config(s3AccessID, s3AccessKey, s3Region, s3Endpoint)
	azureConfig = storage.CreateAzureConfig(azureStorageName, azureStorageKey)
}

type testItem struct {
	path    string
	content string
}

// TESTS
func TestS3Scan(t *testing.T) {
	// Test setup
	filePath := "dir/file1.txt"
	buckerPath := "test/"

	testCache = cache_mock.New()
	scanRequest := getScannerRequest(s3Kind)
	container := InitContainer(s3Kind, s3Config)
	s := scanner.CreateScanner(scanRequest)
	putItems([]testItem{{path: filePath}}, container)

	analyzerServiceMock := getAnalyzeServiceMock(getAnalyzerMockResult())
	datasinkServiceMock := getDatasinkMock(nil)

	// Act
	err := scanner.ScanData(s, scanRequest, testCache, &analyzerServiceMock, &message_types.AnalyzeRequest{}, nil, &datasinkServiceMock)

	// Verify
	item := getItem(filePath, container)
	etag, _ := item.ETag()
	cacheValue, _ := testCache.Get(etag)

	logs := log.ObserverLogs().TakeAll()
	assert.Nil(t, err)
	assert.Equal(t, "test/"+filePath, cacheValue)
	assert.Equal(t, 1, len(logs))
	assert.Equal(t, logs[0].Entry.Message, "2 results were sent to the datasink successfully")
	assert.Equal(t, 1, len(datasinkSrv.Calls))
	// On the second scan the item that was already scan shouldn't be scanned again
	err = scanner.ScanData(s, scanRequest, testCache, &analyzerServiceMock, &message_types.AnalyzeRequest{}, nil, &datasinkServiceMock)
	logs = log.ObserverLogs().TakeAll()
	assert.Nil(t, err)
	assert.Equal(t, 1, len(logs))
	assert.Equal(t, logs[0].Entry.Message, fmt.Sprintf("item %s was already scanned", buckerPath+filePath))
	assert.Equal(t, 1, len(datasinkSrv.Calls))
}

func TestAzureScan(t *testing.T) {
	// Test setup
	filePath := "dir/file1.txt"
	containerPath := "/devstoreaccount1/test/"

	testCache = cache_mock.New()
	scanRequest := getScannerRequest(azureKind)
	container := InitContainer(azureKind, azureConfig)
	putItems([]testItem{{path: filePath}}, container)
	s := scanner.CreateScanner(scanRequest)

	analyzerServiceMock := getAnalyzeServiceMock(getAnalyzerMockResult())
	datasinkServiceMock := getDatasinkMock(nil)

	// Act
	err := scanner.ScanData(s, scanRequest, testCache, &analyzerServiceMock, &message_types.AnalyzeRequest{}, nil, &datasinkServiceMock)

	// Verify
	item := getItem(filePath, container)
	etag, _ := item.ETag()
	cacheValue, _ := testCache.Get(etag)
	logs := log.ObserverLogs().TakeAll()
	assert.Nil(t, err)
	assert.Equal(t, "/devstoreaccount1/test/"+filePath, cacheValue)
	assert.Equal(t, 1, len(logs))
	assert.Equal(t, logs[0].Entry.Message, "2 results were sent to the datasink successfully")
	assert.Equal(t, 1, len(datasinkSrv.Calls))

	// On the second scan the item that was already scan shouldn't be scanned again
	err = scanner.ScanData(s, scanRequest, testCache, &analyzerServiceMock, &message_types.AnalyzeRequest{}, nil, &datasinkServiceMock)
	logs = log.ObserverLogs().TakeAll()
	assert.Nil(t, err)
	assert.Equal(t, 1, len(logs))
	assert.Equal(t, logs[0].Entry.Message, fmt.Sprintf("item %s was already scanned", containerPath+filePath))
	// on the second time the data sink server wasn't called
	assert.Equal(t, 1, len(datasinkSrv.Calls))
}

func TestFileExtension(t *testing.T) {
	filePath := "dir/file1.jpg"
	testCache = cache_mock.New()

	scanRequest := getScannerRequest(azureKind)
	container := InitContainer(azureKind, azureConfig)
	putItems([]testItem{{path: filePath}}, container)
	s := scanner.CreateScanner(scanRequest)

	analyzerServiceMock := getAnalyzeServiceMock(getAnalyzerMockResult())
	datasinkServiceMock := getDatasinkMock(nil)

	// Act
	err := scanner.ScanData(s, scanRequest, testCache, &analyzerServiceMock, &message_types.AnalyzeRequest{}, nil, &datasinkServiceMock)
	assert.Equal(t, err.Error(), "Expected: file extension txt, csv, json, tsv, received: .jpg")
}

func TestSendResultToDatasinkReturnsError(t *testing.T) {
	// Init
	testCache = cache_mock.New()
	filePath := "dir/file1.txt"

	scanRequest := getScannerRequest(azureKind)
	container := InitContainer(azureKind, azureConfig)
	putItems([]testItem{{path: filePath}}, container)
	s := scanner.CreateScanner(scanRequest)

	analyzerServiceMock := getAnalyzeServiceMock(getAnalyzerMockResult())
	datasinkServiceMock := getDatasinkMock(errors.New("some error"))

	// Act
	err := scanner.ScanData(s, scanRequest, testCache, &analyzerServiceMock, &message_types.AnalyzeRequest{}, nil, &datasinkServiceMock)

	// Verify
	assert.EqualValues(t, err.Error(), "some error")
}

func TestResultWrittenToStorage(t *testing.T) {
	// Setup
	containerName = "cloudstoragetest"
	api, _ := storage.New(azureKind, azureConfig, 10)
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

	cloudStorage := cloudStorage.New(datasink)
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
		&message_types.AnalyzeResult{
			Field:       &message_types.FieldTypes{Name: message_types.FieldTypesEnum_EMAIL_ADDRESS.String()},
			Text:        "johnsnow@foo.com",
			Probability: 1.0,
			Location:    location,
		},
	}
	return &message_types.AnalyzeResponse{
		AnalyzeResults: results,
	}
}

func InitContainer(kind string, config stow.ConfigMap) stow.Container {
	api, _ := storage.New(kind, config, 10)
	api.RemoveContainer(containerName)
	return createContainer(api)
}

func getItem(name string, container stow.Container) stow.Item {
	item, _ := container.Item(name)
	return item
}

func createContainer(api *storage.API) stow.Container {
	container, err := api.CreateContainer(containerName)
	if err != nil {
		log.Fatal(err.Error())
	}
	return container
}

func putItems(items []testItem, container stow.Container) {
	for _, item := range items {
		if item.content == "" {
			item.content = "Please call me. My phone number is (555) 253-0000, johnsnow@foo.com"
		}

		_, err := container.Put(item.path, strings.NewReader(item.content), int64(len(item.content)), nil)
		if err != nil {
			log.Fatal(err.Error())
		}
	}
}

func getScannerRequest(kind string) *message_types.ScanRequest {
	if kind == azureKind {
		return &message_types.ScanRequest{
			ScanTemplate: &message_types.ScanTemplate{
				CloudStorageConfig: &message_types.CloudStorageConfig{
					BlobStorageConfig: &message_types.BlobStorageConfig{
						AccountName:   azureStorageName,
						AccountKey:    azureStorageKey,
						ContainerName: containerName,
					},
				},
			},
		}
	}

	return &message_types.ScanRequest{
		ScanTemplate: &message_types.ScanTemplate{
			CloudStorageConfig: &message_types.CloudStorageConfig{
				S3Config: &message_types.S3Config{
					AccessId:   s3AccessID,
					AccessKey:  s3AccessKey,
					Endpoint:   s3Endpoint,
					Region:     s3Region,
					BucketName: containerName,
				},
			},
		},
	}
}

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
