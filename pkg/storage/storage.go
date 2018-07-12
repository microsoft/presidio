package storage

import (
	"fmt"
	"io/ioutil"
	"strings"

	"github.com/korovkin/limiter"
	"github.com/presid-io/stow"
	"github.com/presid-io/stow/azure"
	"github.com/presid-io/stow/s3"

	"github.com/presid-io/presidio/pkg/cache"
	"github.com/presid-io/presidio/pkg/logger"
)

//API storage
type API struct {
	cache    cache.Cache
	location stow.Location
}

//New storage
func New(c cache.Cache, kind string, config stow.Config) (*API, error) {
	location, err := stow.Dial(kind, config)
	if err != nil {
		return &API{}, err
	}
	return &API{cache: c, location: location}, nil
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

//ListObjects list object in bucket/container
func (a *API) ListObjects(container string) error {
	err := stow.WalkContainers(a.location, stow.NoPrefix, 100, func(c stow.Container, err error) error {
		if err != nil {
			return err
		}
		if c.Name() == container {
			logger.Info("Found container " + c.Name())
			err = a.getFiles(c)
			if err != nil {
				return err
			}

		}
		return nil
	})

	return err
}

// walkFunc contain the logic that need to be implemented on each of the items in the container
type walkFunc func(item stow.Item)

// WalkFiles walks over the files in 'container' and executes fn func
func (a *API) WalkFiles(container stow.Container, walkFunc walkFunc) error {
	limit := limiter.NewConcurrencyLimiter(10)

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

func (a *API) getFiles(container stow.Container) error {
	err := stow.Walk(container, stow.NoPrefix, 100, func(item stow.Item, err error) error {
		if err != nil {
			return err
		}
		name, etag, body, size, err1 := a.readObject(item)
		if name == "" || etag == "" || body == "" || size == 0 || err1 != nil {

		}
		return err
	})

	return err
}

func (a *API) readObject(item stow.Item) (string, string, string, int64, error) {
	name := item.Name()
	eTag, _ := item.ETag()
	size, _ := item.Size()
	if a.cache != nil {
		key := eTag
		val, err := a.cache.Get(key)
		if val != "" || err != nil {
			return name, eTag, "", size, err
		}
	}

	r, err := item.Open()
	if err != nil {
		return name, eTag, "", size, err
	}
	defer r.Close()

	body, err := ioutil.ReadAll(r)
	if err != nil {
		return name, eTag, "", size, err
	}

	logger.Info(fmt.Sprintf("Read file %s ETag: %s Size:%d", item.Name(), eTag, size))
	return name, eTag, string(body), size, nil

}
