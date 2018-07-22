package templates

import (
	"encoding/json"
	"fmt"

	message_types "github.com/presid-io/presidio-genproto/golang"
	"github.com/presid-io/presidio/pkg/platform"
)

const separator = "."

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
	result, err := ConvertInterfaceToJSON(message_types.FieldTypesEnum_value)
	return result, err
}

// CreateKey creates template key in the structure: project/action/id
func CreateKey(project string, action string, id string) string {
	key := fmt.Sprintf("%s%s%s%s%s", project, separator, action, separator, id)
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
