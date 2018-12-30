package services

import (
	"encoding/json"
	"fmt"
	"regexp"

	"context"

	types "github.com/Microsoft/presidio-genproto/golang"

	"github.com/Microsoft/presidio/pkg/cache"
	"github.com/Microsoft/presidio/pkg/cache/redis"
	log "github.com/Microsoft/presidio/pkg/logger"
	"github.com/Microsoft/presidio/pkg/platform"
	"github.com/Microsoft/presidio/pkg/presidio"
	"github.com/Microsoft/presidio/pkg/rpc"
)

//Services exposes GRPC services
type Services struct {
	AnalyzerService  types.AnalyzeServiceClient
	AnonymizeService types.AnonymizeServiceClient
	DatasinkService  types.DatasinkServiceClient
	SchedulerService types.SchedulerServiceClient
	Settings         *platform.Settings
}

//New services with settings
func New(settings *platform.Settings) presidio.ServicesAPI {
	svc := Services{Settings: settings}
	return &svc
}

//SetupAnalyzerService GRPC connection
func (services *Services) SetupAnalyzerService() {
	if services.Settings.AnalyzerSvcAddress == "" {
		log.Fatal("analyzer service address is empty")
	}

	analyzeService, err := rpc.SetupAnalyzerService(services.Settings.AnalyzerSvcAddress)
	if err != nil {
		log.Fatal("Connection to analyzer service failed %q", err)
	}

	services.AnalyzerService = analyzeService
}

//SetupAnonymizerService GRPC connection
func (services *Services) SetupAnonymizerService() {

	if services.Settings.AnonymizerSvcAddress == "" {
		log.Fatal("anonymizer service address is empty")
	}

	anonymizeService, err := rpc.SetupAnonymizeService(services.Settings.AnonymizerSvcAddress)
	if err != nil {
		log.Fatal("Connection to anonymizer service failed %q", err)
	}

	services.AnonymizeService = anonymizeService

}

//SetupSchedulerService GRPC connection
func (services *Services) SetupSchedulerService() {

	if services.Settings.SchedulerSvcAddress == "" {
		log.Warn("scheduler service address is empty")
		return
	}

	schedulerService, err := rpc.SetupSchedulerService(services.Settings.SchedulerSvcAddress)
	if err != nil {
		log.Fatal("Connection to anonymizer service failed %q", err)
	}
	services.SchedulerService = schedulerService

}

//SetupDatasinkService GRPC connection
func (services *Services) SetupDatasinkService() {
	address := "localhost"
	datasinkService, err := rpc.SetupDatasinkService(fmt.Sprintf("%s:%d", address, services.Settings.DatasinkGrpcPort))
	if err != nil {
		log.Fatal("Connection to datasink service failed %q", err)
	}

	services.DatasinkService = datasinkService
}

//SetupCache  Redis cache
func (services *Services) SetupCache() cache.Cache {
	if services.Settings.RedisURL == "" {
		log.Fatal("redis address is empty")
	}

	cache := redis.New(
		services.Settings.RedisURL,
		services.Settings.RedisPassword,
		services.Settings.RedisDB,
		services.Settings.RedisSSL,
	)
	return cache
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

//AnonymizeJSON - anonymize text
func (services *Services) AnonymizeJSON(ctx context.Context, jsonToAnonymize string, jsonSchema string, analyzeTemplate *types.AnalyzeTemplate, anonymizeTemplate *types.AnonymizeTemplate) (*types.AnonymizeResponse, error) {
	// Creating the maps for JSON
	schemaMap := map[string]interface{}{}
	valuesMap := map[string]interface{}{}

	// Parsing/Unmarshalling JSON encoding/json
	err := json.Unmarshal([]byte(jsonSchema), &schemaMap)
	if err != nil {
		return nil, err
	}
	err = json.Unmarshal([]byte(jsonToAnonymize), &valuesMap)
	if err != nil {
		return nil, err
	}

	services.parseMap(ctx, schemaMap, valuesMap, analyzeTemplate, anonymizeTemplate)

	anonymizedJSON, err := json.Marshal(valuesMap)

	return &types.AnonymizeResponse{
		Text: string(anonymizedJSON),
	}, err
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

//ApplyStream create stream job
func (services *Services) ApplyStream(ctx context.Context, streamsJobRequest *types.StreamsJobRequest) (*types.StreamsJobResponse, error) {
	return services.SchedulerService.ApplyStream(ctx, streamsJobRequest)
}

//ApplyScan create scan cron job
func (services *Services) ApplyScan(ctx context.Context, scanJobRequest *types.ScannerCronJobRequest) (*types.ScannerCronJobResponse, error) {
	return services.SchedulerService.ApplyScan(ctx, scanJobRequest)
}

//InitDatasink initialize datasink app
func (services *Services) InitDatasink(ctx context.Context, datasinkTemplate *types.DatasinkTemplate) (*types.DatasinkResponse, error) {
	return services.DatasinkService.Init(ctx, datasinkTemplate)
}

//CloseDatasink notify datasink the collector is finished
func (services *Services) CloseDatasink(ctx context.Context, datasinkTemplate *types.CompletionMessage) (*types.DatasinkResponse, error) {
	return services.DatasinkService.Completion(ctx, datasinkTemplate)
}

func (services *Services) analyzeAndAnonymizeJSON(ctx context.Context, val string, field string, analyzeTemplate *types.AnalyzeTemplate, anonymizeTemplate *types.AnonymizeTemplate) string {
	match, _ := regexp.MatchString("<[A-Z]+(_*[A-Z]*)*>", field)
	if match {
		for key := range types.FieldTypesEnum_value {
			fieldName := field[1 : len(field)-1]
			if key == fieldName {
				analyzeResults := services.buildAnalyzeResult(ctx, val, fieldName)
				return services.getAnonymizeResult(ctx, val, anonymizeTemplate, analyzeResults)
			}
		}
	}

	if field == "analyze" {
		analyzeResults, err := services.AnalyzeItem(ctx, val, analyzeTemplate)
		if err != nil {
			return ""
		}
		return services.getAnonymizeResult(ctx, val, anonymizeTemplate, analyzeResults)
	}

	return val
}

func (services *Services) getAnonymizeResult(ctx context.Context, text string, anonymizeTemplate *types.AnonymizeTemplate, analyzeResults []*types.AnalyzeResult) string {
	result, err := services.AnonymizeItem(ctx, analyzeResults, text, anonymizeTemplate)
	if err != nil {
		return ""
	}
	return result.Text
}

func (services *Services) buildAnalyzeResult(ctx context.Context, text string, field string) []*types.AnalyzeResult {
	return [](*types.AnalyzeResult){
		&types.AnalyzeResult{
			Text: text,
			Field: &types.FieldTypes{
				Name: field,
			},
			Score: 1,
			Location: &types.Location{
				Start: 0,
				End:   int32(len(text)),
			},
		},
	}
}

func (services *Services) parseMap(ctx context.Context, schemaMap map[string]interface{}, valuesMap map[string]interface{}, analyzeTemplate *types.AnalyzeTemplate, anonymizeTemplate *types.AnonymizeTemplate) {
	for key, val := range schemaMap {
		switch concreteVal := val.(type) {
		case map[string]interface{}:
			services.parseMap(ctx, val.(map[string]interface{}), (valuesMap[key]).(map[string]interface{}), analyzeTemplate, anonymizeTemplate)
		case []interface{}:
			services.parseArray(ctx, val.([]interface{}), (valuesMap[key]).([]interface{}), analyzeTemplate, anonymizeTemplate)
		default:
			valuesMap[key] = services.analyzeAndAnonymizeJSON(ctx, fmt.Sprint(valuesMap[key]), fmt.Sprint(concreteVal), analyzeTemplate, anonymizeTemplate)
		}
	}
}

func (services *Services) parseArray(ctx context.Context, schemaArray []interface{}, valuesArray []interface{}, analyzeTemplate *types.AnalyzeTemplate, anonymizeTemplate *types.AnonymizeTemplate) {
	for _, val := range schemaArray {
		switch concreteVal := val.(type) {
		case map[string]interface{}:
			for j := range valuesArray {
				services.parseMap(ctx, val.(map[string]interface{}), valuesArray[j].(map[string]interface{}), analyzeTemplate, anonymizeTemplate)
			}
		case []interface{}:
			for j := range valuesArray {
				services.parseArray(ctx, val.([]interface{}), valuesArray[j].([]interface{}), analyzeTemplate, anonymizeTemplate)
			}
		default:
			for j := range valuesArray {
				valuesArray[j] = services.analyzeAndAnonymizeJSON(ctx, fmt.Sprint(valuesArray[j]), fmt.Sprint(concreteVal), analyzeTemplate, anonymizeTemplate)
			}
		}
	}
}
