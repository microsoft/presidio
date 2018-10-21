package presidio

import (
	"fmt"

	"context"

	types "github.com/Microsoft/presidio-genproto/golang"

	log "github.com/Microsoft/presidio/pkg/logger"
	"github.com/Microsoft/presidio/pkg/platform"
	"github.com/Microsoft/presidio/pkg/rpc"
)

var settings *platform.Settings = platform.GetSettings()

//Services exposes GRPC services
type Services struct {
	AnalyzerService  types.AnalyzeServiceClient
	AnonymizeService types.AnonymizeServiceClient
	DatasinkService  types.DatasinkServiceClient
	SchedulerService types.SchedulerServiceClient
}

//SetupAnalyzerService GRPC connection
func (services *Services) SetupAnalyzerService() {
	if settings.AnalyzerSvcAddress == "" {
		log.Fatal("analyzer service address is empty")
	}

	analyzeService, err := rpc.SetupAnalyzerService(settings.AnalyzerSvcAddress)
	if err != nil {
		log.Fatal("Connection to analyzer service failed %q", err)
	}

	services.AnalyzerService = analyzeService
}

//SetupAnonymizerService GRPC connection
func (services *Services) SetupAnonymizerService() {

	if settings.AnonymizerSvcAddress == "" {
		log.Fatal("anonymizer service address is empty")
	}

	anonymizeService, err := rpc.SetupAnonymizeService(settings.AnonymizerSvcAddress)
	if err != nil {
		log.Fatal("Connection to anonymizer service failed %q", err)
	}

	services.AnonymizeService = anonymizeService

}

//SetupSchedulerService GRPC connection
func (services *Services) SetupSchedulerService() {

	if settings.SchedulerSvcAddress == "" {
		log.Warn("scheduler service address is empty")
		return
	}

	schedulerService, err := rpc.SetupSchedulerService(settings.SchedulerSvcAddress)
	if err != nil {
		log.Fatal("Connection to anonymizer service failed %q", err)
	}
	services.SchedulerService = schedulerService

}

//SetupDatasinkService GRPC connection
func (services *Services) SetupDatasinkService() {
	address := "localhost"
	datasinkService, err := rpc.SetupDatasinkService(fmt.Sprintf("%s:%s", address, settings.DatasinkGrpcPort))
	if err != nil {
		log.Fatal("Connection to datasink service failed %q", err)
	}

	services.DatasinkService = datasinkService
}

//AnalyzeItem - search for PII
func (services *Services) AnalyzeItem(ctx context.Context, text string, template *types.AnalyzeTemplate) ([]*types.AnalyzeResult, error) {
	analyzeRequest := &types.AnalyzeRequest{
		AnalyzeTemplate: template,
		Text:            text,
	}

	results, err := services.AnalyzerService.Apply(ctx, analyzeRequest)
	if err != nil {
		return nil, err
	}

	return results.AnalyzeResults, nil
}

//AnonymizeItem - anonymize text
func (services *Services) AnonymizeItem(ctx context.Context, analyzeResults []*types.AnalyzeResult, text string, anonymizeTemplate *types.AnonymizeTemplate) (*types.AnonymizeResponse, error) {
	if anonymizeTemplate != nil {

		anonymizeRequest := &types.AnonymizeRequest{
			Template:       anonymizeTemplate,
			Text:           text,
			AnalyzeResults: analyzeResults,
		}
		res, err := services.AnonymizeService.Apply(ctx, anonymizeRequest)
		return res, err
	}
	return nil, nil
}

//SendResultToDatasink - export results
func (services *Services) SendResultToDatasink(ctx context.Context, analyzeResults []*types.AnalyzeResult,
	anonymizeResults *types.AnonymizeResponse, path string) error {

	for _, element := range analyzeResults {
		// Remove PII from results
		element.Text = ""
	}

	datasinkRequest := &types.DatasinkRequest{
		AnalyzeResults:  analyzeResults,
		AnonymizeResult: anonymizeResults,
		Path:            path,
	}

	_, err := services.DatasinkService.Apply(ctx, datasinkRequest)
	return err
}
