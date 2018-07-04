package storage

import (
	"fmt"
	"io/ioutil"
	"strings"

	"github.com/korovkin/limiter"
	"github.com/presidium-io/stow"
	"github.com/presidium-io/stow/azure"
	"github.com/presidium-io/stow/s3"

	"github.com/presidium-io/presidium/pkg/cache"
	"github.com/presidium-io/presidium/pkg/kv/consul"
	"github.com/presidium-io/presidium/pkg/logger"
	analyzer "github.com/presidium-io/presidium/pkg/modules/analyzer"
	templates "github.com/presidium-io/presidium/pkg/templates"
	message_types "github.com/presidium-io/presidium/pkg/types"
)

//API storage
type API struct {
	cache    cache.Cache
	location stow.Location
	// TODO: need to refactor so storage won't be coupled with the analyzed service
	analyzeService *message_types.AnalyzeServiceClient
}

//New storage
func New(c cache.Cache, kind string, config stow.Config, analyzeService *message_types.AnalyzeServiceClient) (*API, error) {
	location, err := stow.Dial(kind, config)
	if err != nil {
		return &API{}, err
	}
	return &API{cache: c, location: location, analyzeService: analyzeService}, nil
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

type walkFunc func(cache *cache.Cache, container stow.Container, item stow.Item, analyzer *analyzer.Analyzer,
	analyzeRequest *message_types.AnalyzeRequest)

// WalkFiles walks over the files in 'container' and executes fn func
func (a *API) WalkFiles(container stow.Container, fn walkFunc, analyzeKey string) error {
	limit := limiter.NewConcurrencyLimiter(10)
	t := templates.New(consul.New())
	analyzerObj := analyzer.New(a.analyzeService)
	analyzeRequest, err := analyzer.GetAnalyzeRequest(t, analyzeKey)

	if err != nil {
		return err
	}

	err = stow.Walk(container, stow.NoPrefix, 100, func(item stow.Item, err error) error {
		if err != nil {
			return err
		}

		limit.Execute(func() {
			fn(&a.cache, container, item, &analyzerObj, analyzeRequest)
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
