package consul

import (
	"errors"

	"github.com/hashicorp/consul/api"

	"github.com/presidium-io/presidium/pkg/kv"
	"github.com/presidium-io/presidium/pkg/logger"
)

type consul struct {
	kv *api.KV
}

//New Return new KV store
func New() kv.Store {

	config := api.DefaultConfig()
	client, err := api.NewClient(config)
	if err != nil {
		logger.Fatal(err.Error())
	}
	return &consul{
		kv: client.KV(),
	}
}

//PutKVPair insert KV to consul
func (c *consul) PutKVPair(key string, value string) error {
	p := &api.KVPair{Key: key, Value: []byte(value)}
	_, err := c.kv.Put(p, nil)
	return err

}

//GetKVPair get KV from consul
func (c *consul) GetKVPair(key string) (string, error) {
	pair, _, err := c.kv.Get(key, nil)
	if err != nil {
		return "", err
	}
	if pair == nil {
		return "", errors.New("KV not found")
	}
	return string(pair.Value), nil
}

//DeleteKVPair delete KV from consul
func (c *consul) DeleteKVPair(key string) error {
	_, err := c.kv.Delete(key, &api.WriteOptions{})
	return err

}
