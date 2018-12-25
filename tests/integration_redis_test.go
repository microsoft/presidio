// +build functional

package tests

import (
	"github.com/Microsoft/presidio/pkg/cache/redis"
	"github.com/stretchr/testify/assert"
	"testing"
)

const address = "localhost:6379"
const password = ""
const db = 0

func TestRedis(t *testing.T) {

	c := redis.New(address, password, db)

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
	_, err = c.Get(key)
	assert.Error(t, err)

}
