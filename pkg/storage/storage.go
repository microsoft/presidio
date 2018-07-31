package storage

import (
	"bytes"
	"log"
	"strings"

	"github.com/korovkin/limiter"
	"github.com/presid-io/stow"
	"github.com/presid-io/stow/azure"
	"github.com/presid-io/stow/s3"

	message_types "github.com/Microsoft/presidio-genproto/golang"
)

//API storage
type API struct {
	location         stow.Location
	concurrencyLimit int
}

//New initialize a new storage instance.
// Kind is the storage kind: s3/blob storage/ google cloud.
// config holds the storage connection string
// concurrencyLimit is the limit for how many item needs to be scanned at once.
func New(kind string, config stow.Config, concurrencyLimit int) (*API, error) {
	if kind == "azureblob" {
		// Change name kind to match stow expectations
		kind = "azure"
	}
	location, err := stow.Dial(kind, config)
	if err != nil {
		return &API{}, err
	}
	return &API{location: location, concurrencyLimit: concurrencyLimit}, nil
}

//CreateS3Config create S3 configuration
func CreateS3Config(accessKeyID string, secretKey string, region string) (string, stow.ConfigMap) {
	return "s3", stow.ConfigMap{
		s3.ConfigAccessKeyID: accessKeyID,
		s3.ConfigSecretKey:   secretKey,
		s3.ConfigRegion:      region,
	}
}

// InitS3 inits the storage with the supplied credentials
func InitS3(inputConfig *message_types.CloudStorageConfig) (stow.ConfigMap, string) {
	s3AccessKeyID := inputConfig.S3Config.GetAccessId()
	s3SecretKey := inputConfig.S3Config.GetAccessKey()
	s3Region := inputConfig.S3Config.GetRegion()
	s3Bucket := inputConfig.S3Config.GetBucketName()
	if s3AccessKeyID == "" || s3SecretKey == "" || s3Region == "" || s3Bucket == "" {
		log.Fatal("accessId, accessKey, region, bucket must me set for s3 storage kind.")
	}
	_, config := CreateS3Config(s3AccessKeyID, s3SecretKey, s3Region)
	return config, s3Bucket
}

//CreateAzureConfig create azure configuration
func CreateAzureConfig(account string, key string) (string, stow.ConfigMap) {
	return "azureblob", stow.ConfigMap{
		azure.ConfigAccount: account,
		azure.ConfigKey:     key,
	}
}

// InitBlobStorage inits the storage with the supplied credentials
func InitBlobStorage(inputConfig *message_types.CloudStorageConfig) (stow.ConfigMap, string) {
	azureAccountName := inputConfig.BlobStorageConfig.GetAccountName()
	azureAccountKey := inputConfig.BlobStorageConfig.GetAccountKey()
	azureContainer := inputConfig.BlobStorageConfig.GetContainerName()
	if azureAccountKey == "" || azureAccountName == "" || azureContainer == "" {
		log.Fatal("accountName, AccountKey and containerName vars must me set for azure config.")
	}
	_, config := CreateAzureConfig(azureAccountName, azureAccountKey)
	return config, azureContainer
}

// CreateContainer create a container/bucket or return a reference if already exists
func (a *API) CreateContainer(name string) (stow.Container, error) {
	container, err := a.location.CreateContainer(name)
	if err != nil {
		if strings.Contains(err.Error(), "ContainerAlreadyExists") {
			x, err1 := a.location.Container(name)
			return x, err1
		}
		return nil, err
	}
	return container, err
}

// RemoveContainer removes a container/bucket from the storage
func (a *API) RemoveContainer(name string) error {
	return a.location.RemoveContainer(name)
}

//CreatGoogleConfig create google configuration
// func CreatGoogleConfig(configJson string, configProjectId string, configScopes string) (string, stow.ConfigMap) {
// 	return "google", stow.ConfigMap{
// 		google.ConfigJSON:      configJson,
// 		google.ConfigProjectId: configProjectId,
// 		google.ConfigScopes:    configScopes,
// 	}
// }

// walkFunc contain the logic that need to be implemented on each of the items in the container
type walkFunc func(item stow.Item)

// WalkFiles walks over the files in 'container' and executes fn func
func (a *API) WalkFiles(container stow.Container, walkFunc walkFunc) error {
	limit := limiter.NewConcurrencyLimiter(a.concurrencyLimit)

	err := stow.Walk(container, stow.NoPrefix, 100, func(item stow.Item, err error) error {
		if err != nil {
			return err
		}

		limit.Execute(func() {
			walkFunc(item)
		})
		return err
	})
	limit.Wait()

	return err
}

// ReadObject reads the item's content
func ReadObject(item stow.Item) (string, error) {
	reader, err := item.Open()
	if err != nil {
		return "", err
	}

	buf := new(bytes.Buffer)

	if _, err = buf.ReadFrom(reader); err != nil {
		return "", err
	}

	fileContent := buf.String()
	err = reader.Close()

	return fileContent, err
}
