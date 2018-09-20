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
	templates *presidio.Templates
}

//New KV store
func New(s platform.Store) *API {
	template := presidio.New(s)
	return &API{templates: template}
}
