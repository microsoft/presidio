package cloudStorageBinder

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

var (
	// Azure emulator connection string
	storageName = "devstoreaccount1"
	storageKey  = "Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw=="
)

func TestAddActionToFilePath(t *testing.T) {
	path := "/enron/blair-l/sent_items/186..txt"
	newp := addActionToFilePath(path, "action")
	assert.Equal(t, newp, "enron/blair-l/sent_items/186.-action.txt")

	path = "/dir/file"
	newp = addActionToFilePath(path, "action")
	assert.Equal(t, newp, "dir/file-action")

	path = "file"
	newp = addActionToFilePath(path, "action")
	assert.Equal(t, newp, "file-action")
}

// func TestResultWrittenToStorage(t *testing.T) {
// 	// Setup
// 	kind, config := storage.CreateAzureConfig(storageName, storageKey)
// 	api, _ := storage.New(kind, config, 10)
// 	api.RemoveContainer("test")

// 	databinder := &message_types.Databinder{
// 		BindType: "azureblob",
// 		CloudStorageConfig: &message_types.CloudStorageConfig{
// 			BlobStorageConfig: &message_types.BlobStorageConfig{
// 				AccountKey:  storageKey,
// 				AccountName: storageName,
// 			},
// 		},
// 	}

// 	//cloudStorage := New(databinder)
// 	// Act

//}
