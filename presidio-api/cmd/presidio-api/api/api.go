package api

import (
	"github.com/Microsoft/presidio/pkg/cache"
	"github.com/Microsoft/presidio/pkg/platform"
	"github.com/Microsoft/presidio/pkg/presidio"
	"github.com/Microsoft/presidio/pkg/presidio/services"
	"github.com/Microsoft/presidio/pkg/presidio/templates"
)

const (
	//Analyze service
	Analyze = "analyze"
	//Anonymize service
	Anonymize = "anonymize"
	//AnonymizeImage service
	AnonymizeImage = "anonymize-image"
	//Scan service
	Scan = "scan"
	//Stream service
	Stream = "stream"
	//Datasink service
	Datasink = "datasink"
	//ScheduleScannerCronJob service
	ScheduleScannerCronJob = "schedule-scanner-cronjob"
	//ScheduleStreamsJob service
	ScheduleStreamsJob = "schedule-streams-job"
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

//SetupGRPCServices to presidio services
func (api *API) SetupGRPCServices() {
	api.Services.SetupAnalyzerService()
	api.Services.SetupAnonymizerService()
	api.Services.SetupAnonymizerImageService()
	api.Services.SetupSchedulerService()
	api.Services.SetupOCRService()
	api.Services.SetupRecognizerStoreService()
}
