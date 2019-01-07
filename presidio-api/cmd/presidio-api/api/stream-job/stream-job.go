package streamjob

import (
	"context"
	"fmt"

	types "github.com/Microsoft/presidio-genproto/golang"
	"github.com/Microsoft/presidio/pkg/presidio"
	store "github.com/Microsoft/presidio/presidio-api/cmd/presidio-api/api"
	"github.com/Microsoft/presidio/presidio-api/cmd/presidio-api/api/templates"
)

//ScheduleStreamsJob schedule stream job
func ScheduleStreamsJob(ctx context.Context, api *store.API, streamsJobAPIRequest *types.StreamsJobApiRequest, project string) (*types.StreamsJobResponse, error) {

	streamsJobRequest, err := getStreamsJobRequest(api, streamsJobAPIRequest, project)
	if err != nil {
		return nil, err
	}
	schedulerResponse, err := invokeStreamsJobScheduler(ctx, api.Services, streamsJobRequest)
	if err != nil {
		return nil, err
	}

	return schedulerResponse, nil
}

func invokeStreamsJobScheduler(ctx context.Context, services presidio.ServicesAPI, streamsJobRequest *types.StreamsJobRequest) (*types.StreamsJobResponse, error) {
	res, err := services.ApplyStream(ctx, streamsJobRequest)
	if err != nil {
		return nil, err
	}
	return res, nil
}

func getStreamsJobRequest(api *store.API, jobAPIRequest *types.StreamsJobApiRequest, project string) (*types.StreamsJobRequest, error) {
	streamsJobRequest := &types.StreamsJobRequest{}

	if jobAPIRequest.GetStreamsJobTemplateId() != "" {
		jobTemplate := &types.StreamsJobTemplate{}
		err := templates.GetTemplate(api, project, store.ScheduleStreamsJob, jobAPIRequest.StreamsJobTemplateId, jobTemplate)
		if err != nil {
			return nil, err
		}
		streamID := jobTemplate.GetStreamsTemplateId()
		streamTemplate := &types.StreamTemplate{}
		err = templates.GetTemplate(api, project, store.Stream, streamID, streamTemplate)
		if err != nil {
			return nil, err
		}
		if err != nil {
			return nil, err
		}

		datasinkTemplate := &types.DatasinkTemplate{}
		err = templates.GetTemplate(api, project, store.Datasink, jobTemplate.GetDatasinkTemplateId(), datasinkTemplate)
		if err != nil {
			return nil, err
		}
		analyzeTemplate := &types.AnalyzeTemplate{}
		err = templates.GetTemplate(api, project, store.Analyze, jobTemplate.GetAnalyzeTemplateId(), analyzeTemplate)
		if err != nil {
			return nil, err
		}
		anonymizeTemplate := &types.AnonymizeTemplate{}
		if jobTemplate.AnonymizeTemplateId != "" {
			err = templates.GetTemplate(api, project, store.Anonymize, jobTemplate.GetAnonymizeTemplateId(), anonymizeTemplate)
			if err != nil {
				return nil, err
			}
		}

		streamsJobRequest = &types.StreamsJobRequest{
			Name: streamTemplate.GetName(),
			StreamsRequest: &types.StreamRequest{
				AnalyzeTemplate:   analyzeTemplate,
				AnonymizeTemplate: anonymizeTemplate,
				DatasinkTemplate:  datasinkTemplate,
				StreamConfig:      streamTemplate.GetStreamConfig(),
			},
		}
	} else if jobAPIRequest.GetStreamsJobRequest() != nil {
		streamsJobRequest = jobAPIRequest.GetStreamsJobRequest()
	} else {
		return nil, fmt.Errorf("StreamsJobTemplateId or StreamsRequest must be supplied")
	}

	return streamsJobRequest, nil
}
