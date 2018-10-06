package main

import (
	"github.com/Microsoft/presidio/pkg/platform"
	"github.com/Microsoft/presidio/pkg/presidio"
)

const (
	analyze                = "analyze"
	anonymize              = "anonymize"
	scan                   = "scan"
	stream                 = "stream"
	datasink               = "datasink"
	scheduleScannerCronJob = "schedule-scanner-cronjob"
	scheduleStreamsJob     = "schedule-streams-job"
)

//API kv store
type API struct {
	Templates *presidio.Templates
	Services  *presidio.Services
}

//New KV store
func New(s platform.Store) *API {
	template := presidio.New(s)
	return &API{
		Templates: template,
		Services:  &presidio.Services{},
	}
}
