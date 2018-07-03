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

func GetFieldTypes() (string, error) {
	result, err := ConvertInterface2Json(message_types.FieldTypes)
	return result, err
}

func CreateKey(project string, action string, id string) string {
	key := fmt.Sprintf("%s/%s/%s", project, action, id)
	return key
}

func (templates *Templates) GetTemplate(key string) (string, error) {
	return templates.kvStore.GetKVPair(key)
}

func (templates *Templates) InsertTemplate(project string, action string, id string, value string) error {
	key := CreateKey(project, action, id)
	return templates.kvStore.PutKVPair(key, value)
}

func (templates *Templates) UpdateTemplate(project string, action string, id string, value string) error {
	key := CreateKey(project, action, id)
	err := templates.kvStore.DeleteKVPair(key)
	if err != nil {
		return err
	}
	return templates.kvStore.PutKVPair(key, value)
}

func (templates *Templates) DeleteTemplate(project string, action string, id string) error {
	key := CreateKey(project, action, id)
	return templates.kvStore.DeleteKVPair(key)
}

func ConvertInterface2Json(template interface{}) (string, error) {
	b, err := json.Marshal(template)
	if err != nil {
		return "", err
	}
	return string(b), nil
}

func ConvertJSON2Interface(template string, convertTo interface{}) error {
	err := json.Unmarshal([]byte(template), &convertTo)
	return err
}
