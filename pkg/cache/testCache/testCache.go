package testCache

import (
	"github.com/presidium-io/presidium/pkg/cache"
)

type testCache struct {
	c map[string]string
}

//New Return new testCache
func New() cache.Cache {
	return &testCache{
		c: make(map[string]string),
	}
}

//Set key value
func (c *testCache) Set(key string, value string) error {
	cache := *c
	cache.c[key] = value
	return nil
}

//Get key value
func (c *testCache) Get(key string) (string, error) {
	cache := *c
	if val, ok := cache.c[key]; ok {
		return val, nil
	}

	return "", nil
}
