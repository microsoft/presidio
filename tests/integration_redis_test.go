// +build integration

package tests

import (
	"testing"

	"github.com/stretchr/testify/assert"

	"github.com/Microsoft/presidio/pkg/cache/redis"
)

func TestRedis(t *testing.T) {

	address := "localhost:6379"
	password := ""
	db := 0

	c := redis.New(address, password, db, false)
	key := "k.e.y"
	value := "v"

	// Insert value
	err := c.Set(key, value)
	assert.NoError(t, err)

	// Get value
	v, err := c.Get(key)
	assert.NoError(t, err)
	assert.Equal(t, value, v)

	// Delete value
	err = c.Delete(key)
	assert.NoError(t, err)

	// Verify value is deleted
	v1, _ := c.Get(key)
	assert.Equal(t, "", v1)
}
