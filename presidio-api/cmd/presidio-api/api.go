package main

import (
	"github.com/Microsoft/presidio/pkg/cache"
	"github.com/Microsoft/presidio/pkg/platform"
	"github.com/Microsoft/presidio/pkg/presidio"
	"github.com/Microsoft/presidio/pkg/presidio/services"
	"github.com/Microsoft/presidio/pkg/presidio/templates"
)

const (
	analyze                = "analyze"
	anonymize              = "anonymize"
	anonymizeJSON          = "anonymizeJSON"
	scan                   = "scan"
	stream                 = "stream"
	datasink               = "datasink"
	scheduleScannerCronJob = "schedule-scanner-cronjob"
	scheduleStreamsJob     = "schedule-streams-job"
)

//API kv store
type API struct {
	Templates presidio.TemplatesStore
	Services  presidio.ServicesAPI
}

//New KV store
func New(store platform.Store, cacheStore cache.Cache, settings *platform.Settings) *API {
	template := templates.New(store, cacheStore)
	svc := services.New(settings)
	return &API{
		Templates: template,
		Services:  svc,
	}
}
