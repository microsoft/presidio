package presidio

import (
	"fmt"

	types "github.com/Microsoft/presidio-genproto/golang"
	"github.com/Microsoft/presidio/pkg/cache"
	"github.com/Microsoft/presidio/pkg/cache/redis"
	log "github.com/Microsoft/presidio/pkg/logger"
	"github.com/Microsoft/presidio/pkg/platform"
	"github.com/Microsoft/presidio/pkg/rpc"
)

var settings *platform.Settings = platform.GetSettings()

//SetupAnalyzerService GRPC connection
func SetupAnalyzerService() *types.AnalyzeServiceClient {
	if settings.AnalyzerSvcAddress == "" {
		log.Fatal("analyzer service address is empty")
	}

	analyzeService, err := rpc.SetupAnalyzerService(settings.AnalyzerSvcAddress)
	if err != nil {
		log.Fatal("Connection to analyzer service failed %q", err)
	}

	return analyzeService
}

//SetupAnonymizerService GRPC connection
func SetupAnonymizerService() *types.AnonymizeServiceClient {

	if settings.AnonymizerSvcAddress == "" {
		log.Fatal("anonymizer service address is empty")
	}

	anonymizeService, err := rpc.SetupAnonymizeService(settings.AnonymizerSvcAddress)
	if err != nil {
		log.Fatal("Connection to anonymizer service failed %q", err)
	}
	return anonymizeService
}

//SetupSchedulerService GRPC connection
func SetupSchedulerService() *types.SchedulerServiceClient {

	if settings.SchedulerSvcAddress == "" {
		log.Warn("scheduler service address is empty")
		return nil
	}

	schedulerService, err := rpc.SetupSchedulerService(settings.SchedulerSvcAddress)
	if err != nil {
		log.Fatal("Connection to anonymizer service failed %q", err)
	}
	return schedulerService
}

//SetupDatasinkService GRPC connection
func SetupDatasinkService() *types.DatasinkServiceClient {
	address := "localhost"
	datasinkService, err := rpc.SetupDatasinkService(fmt.Sprintf("%s:%s", address, settings.DatasinkGrpcPort))
	if err != nil {
		log.Fatal("Connection to datasink service failed %q", err)
	}

	return datasinkService
}

//SetupCache  Redis cache
func SetupCache() cache.Cache {
	if settings.RedisURL == "" {
		log.Fatal("redis address is empty")
	}

	cache := redis.New(
		settings.RedisURL,
		"", // no password set
		0,  // use default DB
	)
	return cache
}
