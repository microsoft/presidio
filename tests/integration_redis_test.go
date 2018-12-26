// +build functional

package tests

import (
	"os"
	"testing"

	"github.com/stretchr/testify/assert"

	"github.com/Microsoft/presidio/pkg/cache/redis"
)

const address = "localhost:6379"
const password = ""
const db = 0

func init() {
	os.Setenv("LOG_LEVEL", "debug")
}

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
	v1, _ := c.Get(key)
	assert.Equal(t, "", v1)
}
