package redis

import (
	r "github.com/go-redis/redis"

	"github.com/presid-io/presidio/pkg/cache"
)

type redis struct {
	client *r.Client
}

//New Return new Redis cache
func New(address string, password string, db int) cache.Cache {
	return &redis{
		client: r.NewClient(&r.Options{
			Addr:     address,
			Password: password,
			DB:       db,
		}),
	}
}

//Set key value
func (c *redis) Set(key string, value string) error {
	return c.client.Set(key, value, 0).Err()
}

//Get key value
func (c *redis) Get(key string) (string, error) {
	val, err := c.client.Get(key).Result()
	if err == r.Nil {
		return "", nil
	} else if err != nil {
		return "", err
	} else {
		return val, nil
	}
}

func (c *redis) Delete(key string) {
	c.client.Del(key)
}
