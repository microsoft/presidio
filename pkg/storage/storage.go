package storage

import (
	"bytes"
	"fmt"
	"strings"

	log "github.com/Microsoft/presidio/pkg/logger"

	"github.com/korovkin/limiter"
	"github.com/presid-io/stow"
	"github.com/presid-io/stow/azure"
	"github.com/presid-io/stow/s3"

	types "github.com/Microsoft/presidio-genproto/golang"
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
	location, err := stow.Dial(kind, config)
	if err != nil {
		return &API{}, err
	}
	return &API{location: location, concurrencyLimit: concurrencyLimit}, nil
}

// Init cloud storage config
func Init(cloudStorageConfig *types.CloudStorageConfig) (stow.ConfigMap, string, string, error) {
	if cloudStorageConfig.GetBlobStorageConfig() != nil {
		config, containerName := InitBlobStorage(cloudStorageConfig)
		return config, containerName, "azure", nil
	} else if cloudStorageConfig.GetS3Config() != nil {
		config, containerName := InitS3(cloudStorageConfig)
		return config, containerName, "s3", nil
		// } else if cloudStorageConfig.GetGoogleStorageConfig() != nil {
		// 	config, containerName := InitGoogle(cloudStorageConfig)
		// 	return config, containerName, "google", nil
	} else {
		return nil, "", "", fmt.Errorf("storage config is not defined")
	}
}

//CreateS3Config create S3 configuration
func CreateS3Config(accessKeyID string, secretKey string, region string, endpoint string) stow.ConfigMap {
	configMap := stow.ConfigMap{
		s3.ConfigAccessKeyID: accessKeyID,
		s3.ConfigSecretKey:   secretKey,
		s3.ConfigRegion:      region,
	}

	if endpoint != "" {
		configMap.Set(s3.ConfigEndpoint, endpoint)
	}

	return configMap
}

// //CreatGoogleConfig create google configuration
// func CreatGoogleConfig(json string, projectID string, scopes string) (string, stow.ConfigMap) {
// 	return "google", stow.ConfigMap{
// 		google.ConfigJSON:      json,
// 		google.ConfigProjectId: projectID,
// 		google.ConfigScopes:    scopes,
// 	}
// }

// // InitGoogle inits the storage with the supplied parameters
// func InitGoogle(cloudStorageConfig *types.CloudStorageConfig) (stow.ConfigMap, string) {
// 	googleJson := cloudStorageConfig.GoogleStorageConfig.GetJson()
// 	googleProjectID := cloudStorageConfig.GoogleStorageConfig.GetProjectId()
// 	googleScopes := cloudStorageConfig.GoogleStorageConfig.GetScopes()
// 	if googleJson == "" || googleProjectId == "" || googleScopes == "" {
// 		log.Fatal("json, projectId, scopes must me set for google storage kind.")
// 	}
// 	_, config := CreatGoogleConfig(googleJson, googleProjectID, googleScopes)
// 	return config, s3Bucket
// }

// InitS3 inits the storage with the supplied credentials
func InitS3(cloudStorageConfig *types.CloudStorageConfig) (stow.ConfigMap, string) {
	s3AccessKeyID := cloudStorageConfig.S3Config.GetAccessId()
	s3SecretKey := cloudStorageConfig.S3Config.GetAccessKey()
	s3Region := cloudStorageConfig.S3Config.GetRegion()
	s3Bucket := cloudStorageConfig.S3Config.GetBucketName()
	s3Endpoint := cloudStorageConfig.S3Config.GetEndpoint()
	if s3AccessKeyID == "" || s3SecretKey == "" || s3Region == "" || s3Bucket == "" {
		log.Fatal("accessId, accessKey, region, bucket must me set for s3 storage kind.")
	}
	config := CreateS3Config(s3AccessKeyID, s3SecretKey, s3Region, s3Endpoint)
	return config, s3Bucket
}

//CreateAzureConfig create azure configuration
func CreateAzureConfig(account string, key string) stow.ConfigMap {
	return stow.ConfigMap{
		azure.ConfigAccount: account,
		azure.ConfigKey:     key,
	}
}

// InitBlobStorage inits the storage with the supplied credentials
func InitBlobStorage(cloudStorageConfig *types.CloudStorageConfig) (stow.ConfigMap, string) {
	azureAccountName := cloudStorageConfig.BlobStorageConfig.GetAccountName()
	azureAccountKey := cloudStorageConfig.BlobStorageConfig.GetAccountKey()
	azureContainer := cloudStorageConfig.BlobStorageConfig.GetContainerName()
	if azureAccountKey == "" || azureAccountName == "" || azureContainer == "" {
		log.Fatal("accountName, AccountKey and containerName vars must me set for azure config.")
	}

	config := CreateAzureConfig(azureAccountName, azureAccountKey)
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

	n, err := item.Size()
	if err != nil {
		return "", err
	}
	maxFileSizeInBytes := 500000

	// if file size > 0.5Mb trim it
	if n > int64(maxFileSizeInBytes) {
		buf.Truncate(maxFileSizeInBytes)
	}
	fileContent := buf.String()
	err = reader.Close()

	return fileContent, err
}

// PutItem writes a new item to the container
func PutItem(name string, content string, container stow.Container) error {
	r := strings.NewReader(content)
	size := int64(len(content))

	_, err := container.Put(name, r, size, nil)
	return err
}
