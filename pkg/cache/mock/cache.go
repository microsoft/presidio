package mock

import (
	"fmt"

	"github.com/Microsoft/presidio/pkg/cache"
	log "github.com/Microsoft/presidio/pkg/logger"
)

type mockCache struct {
	c map[string]string
}

//New Return new mock cache
func New() cache.Cache {
	return &mockCache{
		c: make(map[string]string),
	}
}

//Set key value
func (c *mockCache) Set(key string, value string) error {
	cache := *c
	cache.c[key] = value
	log.Debug("Mock - Set key %s", key)
	return nil
}

//Get key value
func (c *mockCache) Get(key string) (string, error) {
	cache := *c
	if val, ok := cache.c[key]; ok {
		log.Debug("Mock - Get key %s", key)
		return val, nil
	}

	return "", nil
}

//Delete key value
func (c *mockCache) Delete(key string) error {
	cache := *c
	if _, ok := cache.c[key]; ok {
		log.Debug("Mock - Delete key %s", key)
		delete(cache.c, key)
		return nil
	}

	return fmt.Errorf("Key doesn't exist")
}
