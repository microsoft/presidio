package main

import (
	"github.com/presidium-io/presidium/pkg/kv"
)

type API struct {
	kvStore kv.KVStore
}

//New KV store
func New(s kv.KVStore) *API {
	return &API{kvStore: s}
}
