package scannercronjob

import (
	"context"
	"fmt"

	types "github.com/Microsoft/presidio-genproto/golang"
	"github.com/Microsoft/presidio/pkg/presidio"
	store "github.com/Microsoft/presidio/presidio-api/cmd/presidio-api/api"
	"github.com/Microsoft/presidio/presidio-api/cmd/presidio-api/api/templates"
)

//ScheduleScannerCronJob schedule scanner cron job
func ScheduleScannerCronJob(ctx context.Context, api *store.API, cronAPIJobRequest *types.ScannerCronJobApiRequest, project string) (*types.ScannerCronJobResponse, error) {

	scannerCronJobRequest, err := getScannerCronJobRequest(api, cronAPIJobRequest, project)
	if err != nil {
		return nil, err
	}
	schedulerResponse, err := invokeScannerCronJobScheduler(ctx, api.Services, scannerCronJobRequest)
	if err != nil {
		return nil, err
	}

	return schedulerResponse, nil

}

func invokeScannerCronJobScheduler(ctx context.Context, services presidio.ServicesAPI, scannerCronJobRequest *types.ScannerCronJobRequest) (*types.ScannerCronJobResponse, error) {

	res, err := services.ApplyScan(ctx, scannerCronJobRequest)
	if err != nil {
		return nil, err
	}
	return res, nil
}

func getScannerCronJobRequest(api *store.API, cronJobAPIRequest *types.ScannerCronJobApiRequest, project string) (*types.ScannerCronJobRequest, error) {
	scanRequest := &types.ScanRequest{}
	trigger := &types.Trigger{}
	var name string

	if cronJobAPIRequest.ScannerCronJobTemplateId != "" {
		cronJobTemplate := &types.ScannerCronJobTemplate{}
		templates.GetTemplate(api, project, store.ScheduleScannerCronJob, cronJobAPIRequest.ScannerCronJobTemplateId, cronJobTemplate)

		scanID := cronJobTemplate.ScanTemplateId
		scanTemplate := &types.ScanTemplate{}
		templates.GetTemplate(api, project, store.Scan, scanID, scanTemplate)

		datasinkTemplate := &types.DatasinkTemplate{}
		templates.GetTemplate(api, project, store.Datasink, cronJobTemplate.DatasinkTemplateId, datasinkTemplate)

		analyzeTemplate := &types.AnalyzeTemplate{}
		templates.GetTemplate(api, project, store.Analyze, cronJobTemplate.AnalyzeTemplateId, analyzeTemplate)

		anonymizeTemplate := &types.AnonymizeTemplate{}
		if cronJobTemplate.AnonymizeTemplateId != "" {
			templates.GetTemplate(api, project, store.Anonymize, cronJobTemplate.AnonymizeTemplateId, anonymizeTemplate)
		}
		trigger = cronJobTemplate.GetTrigger()
		name = cronJobTemplate.GetName()
		scanRequest = &types.ScanRequest{
			AnalyzeTemplate:   analyzeTemplate,
			AnonymizeTemplate: anonymizeTemplate,
			DatasinkTemplate:  datasinkTemplate,
			ScanTemplate:      scanTemplate,
		}
	} else if cronJobAPIRequest.ScannerCronJobRequest != nil {
		scanRequest = cronJobAPIRequest.ScannerCronJobRequest.GetScanRequest()
		trigger = cronJobAPIRequest.ScannerCronJobRequest.GetTrigger()
		name = cronJobAPIRequest.ScannerCronJobRequest.GetName()
	} else {
		return nil, fmt.Errorf("ScannerCronJobTemplateId or ScannerCronJobRequest must be supplied")
	}

	return &types.ScannerCronJobRequest{
		Trigger:     trigger,
		ScanRequest: scanRequest,
		Name:        name,
	}, nil
}
