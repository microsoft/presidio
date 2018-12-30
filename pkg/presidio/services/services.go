package services

import (
	"fmt"

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
	AnalyzerService       types.AnalyzeServiceClient
	AnonymizeService      types.AnonymizeServiceClient
	AnonymizeImageService types.AnonymizeImageServiceClient
	OcrService            types.OcrServiceClient
	DatasinkService       types.DatasinkServiceClient
	SchedulerService      types.SchedulerServiceClient
	Settings              *platform.Settings
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

//SetupAnonymizerImageService GRPC connection
func (services *Services) SetupAnonymizerImageService() {

	if services.Settings.AnonymizerImageSvcAddress == "" {
		log.Warn("anonymizer image service address is empty")
		return
	}

	anonymizeImageService, err := rpc.SetupAnonymizeImageService(services.Settings.AnonymizerImageSvcAddress)
	if err != nil {
		log.Fatal("Connection to anonymizer image service failed %q", err)
	}

	services.AnonymizeImageService = anonymizeImageService

}

//SetupOCRService GRPC connection
func (services *Services) SetupOCRService() {

	if services.Settings.OcrSvcAddress == "" {
		log.Warn("ocr service address is empty")
		return
	}

	ocrService, err := rpc.SetupOcrService(services.Settings.OcrSvcAddress)
	if err != nil {
		log.Fatal("Connection to anonymizer service failed %q", err)
	}

	services.OcrService = ocrService

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
func (services *Services) AnonymizeItem(ctx context.Context, analyzeResults []*types.AnalyzeResult,
	text string, anonymizeTemplate *types.AnonymizeTemplate) (*types.AnonymizeResponse, error) {

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

//AnonymizeImageItem - anonymize image
func (services *Services) AnonymizeImageItem(ctx context.Context, image *types.Image, analyzeResults []*types.AnalyzeResult,
	detectionType types.DetectionTypeEnum,
	anonymizeImageTemplate *types.AnonymizeImageTemplate) (*types.AnonymizeImageResponse, error) {

	if anonymizeImageTemplate != nil {

		anonymizeImageRequest := &types.AnonymizeImageRequest{
			Image:          image,
			Template:       anonymizeImageTemplate,
			DetectionType:  detectionType,
			AnalyzeResults: analyzeResults,
		}
		res, err := services.AnonymizeImageService.Apply(ctx, anonymizeImageRequest)
		return res, err
	}
	return nil, nil
}

//OcrItem - ocr image
func (services *Services) OcrItem(ctx context.Context, image *types.Image) (*types.OcrResponse, error) {

	if image.Data != nil {

		ocrRequest := &types.OcrRequest{
			Image: image,
		}
		res, err := services.OcrService.Apply(ctx, ocrRequest)
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
