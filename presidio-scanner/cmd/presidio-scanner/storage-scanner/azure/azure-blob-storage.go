package azure

import (
	"log"

	"github.com/presid-io/stow"

	message_types "github.com/Microsoft/presidio-genproto/golang"
	"github.com/Microsoft/presidio/pkg/storage"
)

// InitBlobStorage inits the storage with the supplied credentials
func InitBlobStorage(inputConfig *message_types.InputConfig) (stow.ConfigMap, string) {
	azureAccountName := inputConfig.BlobStorageConfig.GetAccountName()
	azureAccountKey := inputConfig.BlobStorageConfig.GetAccountKey()
	azureContainer := inputConfig.BlobStorageConfig.GetContainerName()
	if azureAccountKey == "" || azureAccountName == "" || azureContainer == "" {
		log.Fatal("accountName, AccountKey and containerName vars must me set for azure config.")
	}
	_, config := storage.CreateAzureConfig(azureAccountName, azureAccountKey)
	return config, azureContainer
}
