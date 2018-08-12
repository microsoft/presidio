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
	analyzerSvcHost := os.Getenv("ANALYZER_SVC_HOST")
	if analyzerSvcHost == "" {
		log.Fatal("analyzer service address is empty")
	}

	analyzerSvcPort := os.Getenv("ANALYZER_SVC_PORT")
	if analyzerSvcPort == "" {
		log.Fatal("analyzer service port is empty")
	}

	analyzeService, err := rpc.SetupAnalyzerService(fmt.Sprintf("%s:%s", analyzerSvcHost, analyzerSvcPort))
	if err != nil {
		log.Fatal(fmt.Sprintf("Connection to analyzer service failed %q", err))
	}

	return analyzeService
}

//SetupAnoymizerService GRPC connection
func SetupAnoymizerService() *message_types.AnonymizeServiceClient {

	anonymizerSvcHost := os.Getenv("ANONYMIZER_SVC_HOST")
	if anonymizerSvcHost == "" {
		log.Fatal("anonymizer service address is empty")
	}

	anonymizerSvcPort := os.Getenv("ANONYMIZER_SVC_PORT")
	if anonymizerSvcPort == "" {
		log.Fatal("anonymizer service port is empty")
	}

	anonymizeService, err := rpc.SetupAnonymizeService(fmt.Sprintf("%s:%s", anonymizerSvcHost, anonymizerSvcPort))
	if err != nil {
		log.Fatal(fmt.Sprintf("Connection to anonymizer service failed %q", err))
	}
	return anonymizeService
}

//SetupDatasinkService GRPC connection
func SetupDatasinkService() *message_types.DatasinkServiceClient {
	address := "localhost"
	grpcPort := os.Getenv("DATASINK_GRPC_PORT")
	datasinkService, err := rpc.SetupDatasinkService(fmt.Sprintf("%s:%s", address, grpcPort))
	if err != nil {
		log.Fatal(fmt.Sprintf("Connection to datasink service failed %q", err))
	}

	return datasinkService
}

//SetupCache  Redis cache
func SetupCache() cache.Cache {
	redisHost := os.Getenv("REDIS_HOST")
	if redisHost == "" {
		log.Fatal("redis address is empty")
	}

	redisPort := os.Getenv("REDIS_SVC_PORT")
	if redisPort == "" {
		log.Fatal("redis port is empty")
	}

	redisAddress := fmt.Sprintf("%s:%s", redisHost, redisPort)
	cache := redis.New(
		redisAddress,
		"", // no password set
		0,  // use default DB
	)
	return cache
}
