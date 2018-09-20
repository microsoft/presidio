package main

import (
	"github.com/Microsoft/presidio/pkg/platform"
	t "github.com/Microsoft/presidio/pkg/templates"
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
	templates *t.Templates
}

//New KV store
func New(s platform.Store) *API {
	template := t.New(s)
	return &API{templates: template}
}
