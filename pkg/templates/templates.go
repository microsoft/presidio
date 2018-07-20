package templates

import (
	"fmt"

	message_types "github.com/presid-io/presidio-genproto/golang"
	helper "github.com/presid-io/presidio/pkg/helper"
	"github.com/presid-io/presidio/pkg/platform"
)

//Templates kv store
type Templates struct {
	platformStore platform.Store
}

//New KV store
func New(s platform.Store) *Templates {
	return &Templates{platformStore: s}
}

//GetFieldTypes return the available fields
func GetFieldTypes() (string, error) {
	result, err := helper.ConvertInterfaceToJSON(message_types.FieldTypesEnum_value)
	return result, err
}

// CreateKey creates template key in the structure: project/action/id
func CreateKey(project string, action string, id string) string {
	key := fmt.Sprintf("%s/%s/%s", project, action, id)
	return key
}

// GetTemplate from key store
func (templates *Templates) GetTemplate(key string) (string, error) {
	return templates.platformStore.GetKVPair(key)
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
	return templates.platformStore.PutKVPair(key, value)
}

// DeleteTemplate deletes a template from key store
func (templates *Templates) DeleteTemplate(project string, action string, id string) error {
	key := CreateKey(project, action, id)
	return templates.platformStore.DeleteKVPair(key)
}
