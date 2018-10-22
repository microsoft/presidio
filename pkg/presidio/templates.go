package presidio

import (
	"encoding/json"
	"fmt"

	"github.com/Microsoft/presidio/pkg/cache"
	"github.com/Microsoft/presidio/pkg/platform"
)

const separator = "."

//Templates kv store
type Templates struct {
	platformStore platform.Store
	cacheDB       cache.Cache
}

//New KV store
func New(s platform.Store) *Templates {
	cacheClient := cache.InitializeClient(settings.RedisURL, cache.Templates)

	return &Templates{platformStore: s, cacheDB: cacheClient}
}

// CreateKey creates template key in the structure: project/action/id
func CreateKey(project string, action string, id string) string {
	key := fmt.Sprintf("%s%s%s%s%s", project, separator, action, separator, id)
	return key
}

// GetTemplate from key store
func (templates *Templates) GetTemplate(key string) (string, error) {
	// Try getting template from cache
	template, err := templates.cacheDB.Get(key)
	if err != nil {
		return template, nil
	}

	// Try getting template for KV store
	template, err = templates.platformStore.GetKVPair(key)
	if err != nil {
		return "", err
	}

	// Update cache with the retrieved template
	templates.cacheDB.Set(key, template)
	return template, err
}

// InsertTemplate inserts a template to the key store
func (templates *Templates) InsertTemplate(project string, action string, id string, value string) error {
	key := CreateKey(project, action, id)
	return templates.platformStore.PutKVPair(key, value)
}

// UpdateTemplate updates the template in the key store
func (templates *Templates) UpdateTemplate(project string, action string, id string, value string) error {
	key := CreateKey(project, action, id)
	err := templates.platformStore.DeleteKVPair(key)
	if err != nil {
		return err
	}

	// Expire current cached item (if exists)
	// Expire is chosen over Del as Expire invalidates the cached item
	// in a lazy manner.
	templates.cacheDB.Expire(key)

	return templates.platformStore.PutKVPair(key, value)
}

// DeleteTemplate deletes a template from key store
func (templates *Templates) DeleteTemplate(project string, action string, id string) error {
	key := CreateKey(project, action, id)

	// Expire current cached item (if exists)
	// Expire is chosen over Del as Expire invalidates the cached item
	// in a lazy manner.
	templates.cacheDB.Expire(key)

	return templates.platformStore.DeleteKVPair(key)
}

// ConvertJSONToInterface convert Json to go Interface
func ConvertJSONToInterface(template string, convertTo interface{}) error {
	err := json.Unmarshal([]byte(template), &convertTo)
	return err
}

// ConvertInterfaceToJSON convert go interface to json
func ConvertInterfaceToJSON(template interface{}) (string, error) {
	b, err := json.Marshal(template)
	if err != nil {
		return "", err
	}
	return string(b), nil
}
