package main

import (
	"os"
	"strconv"

	log "github.com/presidium-io/presidium/pkg/logger"
	sd "github.com/presidium-io/presidium/pkg/service-discovery"
	"github.com/presidium-io/presidium/pkg/service-discovery/consul"
)

var (
	analyzerSvcHost = os.Getenv("ANALYZER_SVC_HOST")
	analyzerSvcPort = os.Getenv("ANALYZER_SVC_PORT")

	anonymizerSvcHost = os.Getenv("ANONYMIZER_SVC_HOST")
	anonymizerSvcPort = os.Getenv("ANONYMIZER_SVC_PORT")

	redisHost = os.Getenv("REDIS_HOST")
	redisPort = os.Getenv("REDIS_PORT")
)

func main() {

	if analyzerSvcHost == "" || analyzerSvcPort == "" || anonymizerSvcHost == "" || anonymizerSvcPort == "" || redisHost == "" || redisPort == "" {
		log.Fatal("ANALYZER_SVC_HOST, ANALYZER_SVC_PORT, ANONYMIZER_SVC_HOST, ANONYMIZER_SVC_PORT, REDIS_HOST, REDIS_PORT env vars must me set.")
	}

	store := consul.New()
	err := registerService(store, "analyzer", analyzerSvcHost, analyzerSvcPort)
	if err != nil {
		log.Fatal(err.Error())
	}
	err = registerService(store, "anonymizer", anonymizerSvcHost, anonymizerSvcPort)
	if err != nil {
		log.Fatal(err.Error())
	}
	err = registerService(store, "redis", redisHost, redisPort)
	if err != nil {
		log.Fatal(err.Error())
	}
}

func registerService(store sd.Store, name string, address string, sport string) error {
	port, err := strconv.Atoi(sport)
	if err != nil {
		return err
	}

	err = store.Register(name, address, port)
	return err
}
