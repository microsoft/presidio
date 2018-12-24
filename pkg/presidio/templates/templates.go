package templates

import (
	"fmt"

	"github.com/Microsoft/presidio/pkg/platform"
	"github.com/Microsoft/presidio/pkg/presidio"
)

const separator = "."

//Templates kv store
type Templates struct {
	platformStore platform.Store
}

//New KV store
func New(s platform.Store) presidio.TemplatesStore {
	return &Templates{platformStore: s}
}

// createKey creates template key in the structure: project/action/id
func createKey(project string, action string, id string) string {
	key := fmt.Sprintf("%s%s%s%s%s", project, separator, action, separator, id)
	return key
}

// GetTemplate from key store
func (templates *Templates) GetTemplate(project string, action string, id string) (string, error) {
	key := createKey(project, action, id)
	return templates.platformStore.GetKVPair(key)
}

// InsertTemplate inserts a template to the key store
func (templates *Templates) InsertTemplate(project string, action string, id string, value string) error {
	key := createKey(project, action, id)
	return templates.platformStore.PutKVPair(key, value)
}

// UpdateTemplate updates the template in the key store
func (templates *Templates) UpdateTemplate(project string, action string, id string, value string) error {
	key := createKey(project, action, id)
	err := templates.platformStore.DeleteKVPair(key)
	if err != nil {
		return err
	}
	return templates.platformStore.PutKVPair(key, value)
}

// DeleteTemplate deletes a template from key store
func (templates *Templates) DeleteTemplate(project string, action string, id string) error {
	key := createKey(project, action, id)
	return templates.platformStore.DeleteKVPair(key)
}
