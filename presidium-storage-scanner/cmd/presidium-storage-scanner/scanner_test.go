package main

import (
	"bytes"
	"context"
	"fmt"
	"log"
	"os"
	"strings"
	"testing"

	"github.com/presidium-io/stow"
	"github.com/stretchr/testify/mock"
	"google.golang.org/grpc"

	"github.com/stretchr/testify/assert"

	message_types "github.com/presidium-io/presidium-genproto/golang"
	c "github.com/presidium-io/presidium/pkg/cache"
	cache_mock "github.com/presidium-io/presidium/pkg/cache/mock"
	"github.com/presidium-io/presidium/pkg/modules/analyzer"
	"github.com/presidium-io/presidium/pkg/storage"
)

var (
	// Azure emulator connection string
	storageName = "devstoreaccount1"
	storageKey  = "Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw=="
	testCache   c.Cache
	serviceMock analyzer.Analyzer
)

type MyMockedObject struct {
	mock.Mock
}

func (m *MyMockedObject) InvokeAnalyze(c context.Context, analyzeRequest *message_types.AnalyzeRequest, text string) (*message_types.AnalyzeResponse, error) {
	args := m.Mock.Called()
	y := args.Get(0).(*message_types.AnalyzeResponse)
	return y, args.Error(1)
}

func (m *MyMockedObject) Apply(ctx context.Context, in *message_types.DatabinderRequest, opts ...grpc.CallOption) (*message_types.DatabinderResponse, error) {
	args := m.Mock.Called()
	var result *message_types.DatabinderResponse
	if args.Get(0) != nil {
		result = args.Get(0).(*message_types.DatabinderResponse)
	}
	return result, args.Error(1)
}

func TestAzureScanAndAnalyze(t *testing.T) {
	testCache = cache_mock.New()
	kind, config := storage.CreateAzureConfig(storageName, storageKey)

	analyzerObj := &MyMockedObject{}
	serviceMock = analyzerObj
	analyzerObj.On("InvokeAnalyze", mock.Anything, mock.Anything, mock.Anything).Return(getAnalyzerMockResult(), nil)

	api, _ := storage.New(testCache, kind, config)
	container := createContainer(api)
	putItem("file1.txt", container, api)

	// Set log output
	var buf bytes.Buffer
	log.SetOutput(&buf)
	defer func() {
		log.SetOutput(os.Stderr)
	}()

	// Act
	api.WalkFiles(container, scanFile)

	// validate output
	assert.Contains(t, buf.String(), "Found: \"name:\\\"PHONE_NUMBER\\\" \", propability: 1.000000, Location: start:153 end:163 length:10")
	api.WalkFiles(container, scanFile)
	assert.Contains(t, buf.String(), "Item was already scanned file1.txt")

	// test cleanup
	api.RemoveContainer("test")
}

func TestFileExtension(t *testing.T) {
	// Setup
	testCache := cache_mock.New()
	kind, config := storage.CreateAzureConfig(storageName, storageKey)

	analyzerObj := &MyMockedObject{}
	serviceMock = analyzerObj

	api, _ := storage.New(testCache, kind, config)
	container := createContainer(api)
	putItem("file1.jpg", container, api)

	// Set log output
	var buf bytes.Buffer
	log.SetOutput(&buf)
	defer func() {
		log.SetOutput(os.Stderr)
	}()

	// Act
	api.WalkFiles(container, scanFile)

	// Assert
	assert.Contains(t, buf.String(), "Expected: file extension txt, csv, json, tsv, received: .jpg")

	// test cleanup
	api.RemoveContainer("test")
}

func TestSendResultToDataBinder(t *testing.T) {
	// Setup
	testCache = cache_mock.New()
	kind, config := storage.CreateAzureConfig(storageName, storageKey)
	api, _ := storage.New(testCache, kind, config)

	container := createContainer(api)
	item := putItem("file1.jpg", container, api)

	etag, _ := item.ETag()
	testCache.Set(etag, item.Name())
	dataBinderSrv := &MyMockedObject{}
	var databinderMock message_types.DatabinderServiceClient = dataBinderSrv
	dataBinderSrv.On("Apply", mock.Anything, mock.Anything, mock.Anything).Return(nil, fmt.Errorf("some error"))

	// Actk
	sendResultToDataBinder(item, getAnalyzerMockResult().AnalyzeResults, testCache, &databinderMock)

	// Assert
	val, _ := testCache.Get(etag)
	assert.Empty(t, val)
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

func scanFile(item stow.Item) {
	var analyzeRequest *message_types.AnalyzeRequest
	ScanAndAnalyze(&testCache, item, &serviceMock, analyzeRequest)
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

	// Add data to
	md1 := map[string]interface{}{"stowmetadata": "foo"}
	item, err := container.Put(itemName, strings.NewReader(content), int64(len(content)), md1)
	if err != nil {
		log.Fatal(err.Error())
	}
	return item
}
