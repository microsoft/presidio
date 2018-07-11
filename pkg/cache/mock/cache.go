package mock

import (
	"github.com/presid-io/presidio/pkg/cache"
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
	return nil
}

//Get key value
func (c *mockCache) Get(key string) (string, error) {
	cache := *c
	if val, ok := cache.c[key]; ok {
		return val, nil
	}

	return "", nil
}
