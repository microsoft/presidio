package storage

import (
	"fmt"
	"io/ioutil"

	"github.com/graymeta/stow"
	"github.com/graymeta/stow/azure"
	"github.com/graymeta/stow/s3"

	"github.com/presidium-io/presidium/pkg/cache"
	"github.com/presidium-io/presidium/pkg/logger"
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
