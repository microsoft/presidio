package scanner

import (
	"bytes"
	"context"
	"log"
	"os"
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"

	"github.com/presidium-io/presidium/pkg/cache/testCache"
	"github.com/presidium-io/presidium/pkg/storage"
	message_types "github.com/presidium-io/presidium/pkg/types"
	"github.com/presidium-io/stow"
	"github.com/stretchr/testify/mock"
)

var (
	// Azure emulator connection string
	storageName = "devstoreaccount1"
	storageKey  = "Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw=="
	kind        = "azure"
)

type MyMockedObject struct {
	mock.Mock
}

func (m *MyMockedObject) Apply(ctx context.Context, in *message_types.AnalyzeRequest, opts ...grpc.CallOption) (*message_types.Results, error) {
	return nil, nil
}

func TestAzureScanAndAnalyze(t *testing.T) {
	var testCache = testCache.New()
	kind, config := storage.CreateAzureConfig(storageName, storageKey)

	analyzeService := &MyMockedObject{}
	location := &message_types.Location{
		Start: 153, End: 163, Length: 10,
	}
	result := [](*message_types.Result){
		&message_types.Result{
			FieldType:   "PHONE_NUMBER",
			Value:       "(555) 253-0000",
			Probability: 1.0,
			Location:    location,
		},
	}
	results := &message_types.Results{
		Results: result,
	}
	content := "Please call me. My phone number is (555) 253-0000."
	var serviceMock message_types.AnalyzeServiceClient = analyzeService
	analyzeService.On("Apply", mock.Anything, mock.Anything).Return(results)

	api, _ := storage.New(testCache, kind, config, &serviceMock)

	container, err := api.CreateContainer("test")
	if err != nil {
		log.Fatal(err.Error())
	}

	md1 := map[string]interface{}{"stowmetadata": "foo"}
	container.Put("file1", strings.NewReader(content), int64(len(content)), md1)

	var buf bytes.Buffer
	log.SetOutput(&buf)
	defer func() {
		log.SetOutput(os.Stderr)
	}()

	err = stow.Walk(container, stow.CursorStart, 100, func(item stow.Item, err error) error {
		if err != nil {
			return err
		}
		ScanAndAnalyze(&testCache, container, item, &serviceMock)

		return nil
	})
	t.Log(buf.String())
	if err != nil {
		log.Fatal(err.Error())
		return
	}
	assert.Equal(t, storageName, storageKey)
}
