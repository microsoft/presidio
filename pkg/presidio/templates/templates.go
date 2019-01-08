package templates

import (
	"fmt"

	"github.com/Microsoft/presidio/pkg/cache"
	log "github.com/Microsoft/presidio/pkg/logger"
	"github.com/Microsoft/presidio/pkg/platform"

	"github.com/Microsoft/presidio/pkg/presidio"
)

const separator = "."

//Templates kv store
type Templates struct {
	platformStore platform.Store
	cacheStore    cache.Cache
}

//New KV store
func New(s platform.Store, c cache.Cache) presidio.TemplatesStore {

	return &Templates{
		platformStore: s,
		cacheStore:    c}
}

// createKey creates template key in the structure: project/action/id
func createKey(project, action, id string) (string, error) {
	if project == "" || action == "" || id == "" {
		return "", fmt.Errorf("Invalid key")
	}
	key := fmt.Sprintf("%s%s%s%s%s", project, separator, action, separator, id)
	return key, nil
}

// GetTemplate from key store
func (templates *Templates) GetTemplate(project, action, id string) (string, error) {
	key, err := createKey(project, action, id)
	if err != nil {
		return "", err
	}
	if templates.cacheStore != nil {
		res, err := templates.cacheStore.Get(key)
		if res != "" && err == nil {
			return res, err
		}
	}
	return templates.platformStore.GetKVPair(key)
}

// InsertTemplate inserts a template to the key store
func (templates *Templates) InsertTemplate(project, action, id, value string) error {
	key, err := createKey(project, action, id)
	if err != nil {
		return err
	}
	if templates.cacheStore != nil {
		err := templates.cacheStore.Set(key, value)
		if err != nil {
			log.Error(err.Error())
		}
	}
	return templates.platformStore.PutKVPair(key, value)
}

// UpdateTemplate updates the template in the key store
func (templates *Templates) UpdateTemplate(project, action, id, value string) error {
	key, err := createKey(project, action, id)
	if err != nil {
		return err
	}

	if templates.cacheStore != nil {
		err := templates.cacheStore.Delete(key)
		if err != nil {
			log.Error(err.Error())
		}
		err = templates.cacheStore.Set(key, value)
		if err != nil {
			log.Error(err.Error())
		}
	}
	err = templates.platformStore.DeleteKVPair(key)
	if err != nil {
		return err
	}
	return templates.platformStore.PutKVPair(key, value)
}

// DeleteTemplate deletes a template from key store
func (templates *Templates) DeleteTemplate(project, action, id string) error {
	key, err := createKey(project, action, id)
	if err != nil {
		return err
	}
	if templates.cacheStore != nil {
		err := templates.cacheStore.Delete(key)
		if err != nil {
			log.Error(err.Error())
		}
	}
	return templates.platformStore.DeleteKVPair(key)
}
