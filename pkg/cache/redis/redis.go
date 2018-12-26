package redis

import (
	"crypto/tls"

	r "github.com/go-redis/redis"

	"github.com/Microsoft/presidio/pkg/cache"
	log "github.com/Microsoft/presidio/pkg/logger"
)

type redis struct {
	client *r.Client
}

//New Return new Redis cache
func New(address string, password string, db int, ssl bool) cache.Cache {

	if ssl {
		return &redis{
			client: r.NewClient(&r.Options{
				Addr:      address,
				Password:  password,
				DB:        db,
				TLSConfig: &tls.Config{InsecureSkipVerify: true},
			})}
	}
	return &redis{
		client: r.NewClient(&r.Options{
			Addr:     address,
			Password: password,
			DB:       db,
		})}

}

//Set key value
func (c *redis) Set(key string, value string) error {
	err := c.client.Set(key, value, 0).Err()
	log.Debug("Redis - Set key %s", key)
	return err
}

//Get key value
func (c *redis) Get(key string) (string, error) {
	val, err := c.client.Get(key).Result()
	log.Debug("Redis - Get key %s", key)
	if err == r.Nil {
		return "", nil
	} else if err != nil {
		return "", err
	} else {
		return val, nil
	}
}

//Delete key
func (c *redis) Delete(key string) error {
	err := c.client.Del(key).Err()
	log.Debug("Redis - Delete key %s", key)
	return err
}
