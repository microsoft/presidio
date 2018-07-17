package azure

import (
	"log"
	"os"

	"github.com/presid-io/stow"

	"github.com/presid-io/presidio/pkg/storage"
)

// InitBlobStorage inits the storage with the supplied credentials
func InitBlobStorage() (stow.ConfigMap, string) {
	azureAccountName := os.Getenv("AZURE_ACCOUNT")
	azureAccountKey := os.Getenv("AZURE_KEY")
	azureContainer := os.Getenv("AZURE_CONTAINER")
	if azureAccountKey == "" || azureAccountName == "" || azureContainer == "" {
		log.Fatal("AZURE_ACCOUNT, AZURE_KEY, AZURE_CONTAINER env vars must me set.")
	}
	_, config := storage.CreateAzureConfig(azureAccountName, azureAccountKey)
	return config, azureContainer
}
