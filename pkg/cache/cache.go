package cache

import (
	"log"

	"github.com/Microsoft/presidio/pkg/cache/redis"
)

//Cache interface
type Cache interface {
	Set(key string, value string) error
	Get(key string) (string, error)
	Expire(key string)
}

//DBIndex represents the cache db ids
type DBIndex int

const (
	//Scanner db
	Scanner DBIndex = 0
	//Templates db
	Templates DBIndex = 1
)

//InitializeClient New Redis cache instance
func InitializeClient(redisURL string, index DBIndex) Cache {
	if redisURL == "" {
		log.Fatal("redis address is empty")
	}

	cache := redis.New(
		redisURL,
		"", // no password set
		int(index),
	)
	return cache
}
