package cloudStorageBinder

import (
	"strings"
	"testing"

	"github.com/presid-io/stow"
	"github.com/stretchr/testify/assert"

	message_types "github.com/Microsoft/presidio-genproto/golang"
	"github.com/Microsoft/presidio/pkg/storage"
	"github.com/Microsoft/presidio/pkg/templates"
)

var (
	// Azure emulator connection string
	storageName = "devstoreaccount1"
	storageKey  = "Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw=="
)

func TestAddActionToFilePath(t *testing.T) {
	path := "/dir1/dir2/dir3/filename.txt"
	newp := addActionToFilePath(path, "action")
	assert.Equal(t, newp, "dir1/dir2/dir3/filename-action.txt")

	path = "/dir/file"
	newp = addActionToFilePath(path, "action")
	assert.Equal(t, newp, "dir/file-action")

	path = "file"
	newp = addActionToFilePath(path, "action")
	assert.Equal(t, newp, "file-action")
}

func TestResultWrittenToStorage(t *testing.T) {
	// Setup
	containerName := "cloudstoragetest"
	kind, config := storage.CreateAzureConfig(storageName, storageKey)
	api, _ := storage.New(kind, config, 10)
	api.RemoveContainer(containerName)

	databinder := &message_types.Databinder{
		CloudStorageConfig: &message_types.CloudStorageConfig{
			BlobStorageConfig: &message_types.BlobStorageConfig{
				AccountKey:    storageKey,
				AccountName:   storageName,
				ContainerName: containerName,
			},
		},
	}

	cloudStorage := New(databinder, "azureblob")
	resultsPath := "someDir/SomeFile.txt"
	anonymizeResponse := &message_types.AnonymizeResponse{
		Text: "<Person> live is <Location>",
	}
	//Act
	cloudStorage.WriteAnalyzeResults(getAnalyzerMockResult(), resultsPath)
	cloudStorage.WriteAnonymizeResults(anonymizeResponse, resultsPath)

	//Verify
	container, _ := api.CreateContainer(containerName)
	count := 0

	api.WalkFiles(container, func(item stow.Item) {
		count++
		if strings.Contains(item.Name(), "analyzed") {
			analyzedFile, _ := storage.ReadObject(item)
			expectedContent, _ := templates.ConvertInterfaceToJSON(getAnalyzerMockResult())
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

func getAnalyzerMockResult() []*message_types.AnalyzeResult {
	return [](*message_types.AnalyzeResult){
		&message_types.AnalyzeResult{
			Field:       &message_types.FieldTypes{Name: message_types.FieldTypesEnum_PHONE_NUMBER.String()},
			Text:        "(555) 253-0000",
			Probability: 1.0,
			Location: &message_types.Location{
				Start: 153, End: 163, Length: 10,
			},
		},
		&message_types.AnalyzeResult{
			Field:       &message_types.FieldTypes{Name: message_types.FieldTypesEnum_PERSON.String()},
			Text:        "John Smith",
			Probability: 0.8,
			Location: &message_types.Location{
				Start: 180, End: 190, Length: 10,
			},
		},
	}
}
