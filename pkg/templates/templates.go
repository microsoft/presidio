package templates

import (
	"fmt"

	"encoding/json"

	"github.com/presidium-io/presidium/pkg/kv"
	message_types "github.com/presidium-io/presidium/pkg/types"
)

//Templates kv store
type Templates struct {
	kvStore kv.Store
}

//New KV store
func New(s kv.Store) *Templates {
	return &Templates{kvStore: s}
}

//GetFieldTypes return the available fields
func GetFieldTypes() (string, error) {
	result, err := ConvertInterfaceToJSON(message_types.FieldTypes)
	return result, err
}

// CreateKey creates template key in the structure: project/action/id
func CreateKey(project string, action string, id string) string {
	key := fmt.Sprintf("%s/%s/%s", project, action, id)
	return key
}

// GetTemplate from key store
func (templates *Templates) GetTemplate(key string) (string, error) {
	return templates.kvStore.GetKVPair(key)
}

// InsertTemplate inserts a template to the key store
func (templates *Templates) InsertTemplate(project string, action string, id string, value string) error {
	key := CreateKey(project, action, id)
	return templates.kvStore.PutKVPair(key, value)
}

// UpdateTemplate updates the template in the key store
func (templates *Templates) UpdateTemplate(project string, action string, id string, value string) error {
	key := CreateKey(project, action, id)
	err := templates.kvStore.DeleteKVPair(key)
	if err != nil {
		return err
	}
	return templates.kvStore.PutKVPair(key, value)
}

// DeleteTemplate deletes a template from key store
func (templates *Templates) DeleteTemplate(project string, action string, id string) error {
	key := CreateKey(project, action, id)
	return templates.kvStore.DeleteKVPair(key)
}

// ConvertInterfaceToJSON convert go interface to json
func ConvertInterfaceToJSON(template interface{}) (string, error) {
	b, err := json.Marshal(template)
	if err != nil {
		return "", err
	}
	return string(b), nil
}

// ConvertJSONToInterface convert Json to go Interface
func ConvertJSONToInterface(template string, convertTo interface{}) error {
	err := json.Unmarshal([]byte(template), &convertTo)
	return err
}
