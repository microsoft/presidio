package main

import (
	"github.com/presid-io/presidio/pkg/platform"
	t "github.com/presid-io/presidio/pkg/templates"
)

//API kv store
type API struct {
	templates *t.Templates
}

//New KV store
func New(s platform.Store) *API {
	template := t.New(s)
	return &API{templates: template}
}
