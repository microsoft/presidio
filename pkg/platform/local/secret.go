package local

import (
	"io/ioutil"
	"os"
	"path"
)

func (s *store) GetKVPair(key string) (string, error) {
	filepath := path.Join(s.path, key)
	value, err := ioutil.ReadFile(filepath)
	return string(value), err
}

func (s *store) PutKVPair(key string, value string) error {
	filepath := path.Join(s.path, key)
	err := ioutil.WriteFile(filepath, []byte(value), 0666)
	return err
}

func (s *store) DeleteKVPair(key string) error {
	filepath := path.Join(s.path, key)
	return os.Remove(filepath)
}
