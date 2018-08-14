package presidio

import (
	"fmt"
	"os"

	message_types "github.com/Microsoft/presidio-genproto/golang"
	"github.com/Microsoft/presidio/pkg/cache"
	"github.com/Microsoft/presidio/pkg/cache/redis"
	log "github.com/Microsoft/presidio/pkg/logger"
	"github.com/Microsoft/presidio/pkg/rpc"
)

//SetupAnalyzerService GRPC connection
func SetupAnalyzerService() *message_types.AnalyzeServiceClient {
	analyzerSvcAddress := os.Getenv("ANALYZER_SVC_ADDRESS")
	if analyzerSvcAddress == "" {
		log.Fatal("analyzer service address is empty")
	}

	analyzeService, err := rpc.SetupAnalyzerService(analyzerSvcAddress)
	if err != nil {
		log.Fatal("Connection to analyzer service failed %q", err)
	}

	return analyzeService
}

//SetupAnoymizerService GRPC connection
func SetupAnoymizerService() *message_types.AnonymizeServiceClient {

	anonymizerSvcAddress := os.Getenv("ANONYMIZER_SVC_ADDRESS")
	if anonymizerSvcAddress == "" {
		log.Fatal("anonymizer service address is empty")
	}

	anonymizeService, err := rpc.SetupAnonymizeService(anonymizerSvcAddress)
	if err != nil {
		log.Fatal("Connection to anonymizer service failed %q", err)
	}
	return anonymizeService
}

//SetupSchedulerService GRPC connection
func SetupSchedulerService() *message_types.SchedulerServiceClient {

	schedulerAddress := os.Getenv("SCHEDULER_SVC_ADDRESS")
	if schedulerAddress == "" {
		log.Warn("scheduler service address is empty")
		return nil
	}

	schedulerService, err := rpc.SetupSchedulerService(schedulerAddress)
	if err != nil {
		log.Fatal("Connection to anonymizer service failed %q", err)
	}
	return schedulerService
}

//SetupDatasinkService GRPC connection
func SetupDatasinkService() *message_types.DatasinkServiceClient {
	address := "localhost"
	grpcPort := os.Getenv("DATASINK_GRPC_PORT")
	datasinkService, err := rpc.SetupDatasinkService(fmt.Sprintf("%s:%s", address, grpcPort))
	if err != nil {
		log.Fatal("Connection to datasink service failed %q", err)
	}

	return datasinkService
}

//SetupCache  Redis cache
func SetupCache() cache.Cache {
	redisURL := os.Getenv("REDIS_URL")
	if redisURL == "" {
		log.Fatal("redis address is empty")
	}

	cache := redis.New(
		redisURL,
		"", // no password set
		0,  // use default DB
	)
	return cache
}
