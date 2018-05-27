package main

import (
	"github.com/presidium-io/presidium/pkg/kv"
)

//API kv store
type API struct {
	kvStore kv.Store
}

//New KV store
func New(s kv.Store) *API {
	return &API{kvStore: s}
}
