package storage

import (
	"bytes"
	"strings"

	"github.com/korovkin/limiter"
	"github.com/presid-io/stow"
	"github.com/presid-io/stow/azure"
	"github.com/presid-io/stow/s3"

	analyzer "github.com/presid-io/presidio/pkg/modules/analyzer"
	"github.com/presid-io/presidio/pkg/platform"
	templates "github.com/presid-io/presidio/pkg/templates"
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

//CreateS3Config create S3 configuration
func CreateS3Config(accessKeyID string, secretKey string, region string) (string, stow.ConfigMap) {
	return "s3", stow.ConfigMap{
		s3.ConfigAccessKeyID: accessKeyID,
		s3.ConfigSecretKey:   secretKey,
		s3.ConfigRegion:      region,
	}
}

//CreateAzureConfig create azure configuration
func CreateAzureConfig(account string, key string) (string, stow.ConfigMap) {
	return "azure", stow.ConfigMap{
		azure.ConfigAccount: account,
		azure.ConfigKey:     key,
	}
}

// CreateContainer create a container/bucket or return a reference if already exists
func (a *API) CreateContainer(name string) (stow.Container, error) {
	container, err := a.location.CreateContainer(name)
	if err != nil {
		if strings.Contains(err.Error(), "ContainerAlreadyExists") {
			x, _ := a.location.Container(name)
			return x, nil
		}
		return nil, err
	}
	return container, nil
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
func (a *API) WalkFiles(container stow.Container, fn walkFunc, analyzeKey string, store platform.Store) error {
	limit := limiter.NewConcurrencyLimiter(a.concurrencyLimit)

	t := templates.New(store)
	analyzerObj := analyzer.New(a.analyzeService)
	analyzeRequest, err := analyzer.GetAnalyzeRequest(t, analyzeKey)

	if err != nil {
		return err
	}

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
