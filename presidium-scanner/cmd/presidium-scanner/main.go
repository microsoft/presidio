package main

import (
	"fmt"
	"log"
	"os"

	"github.com/graymeta/stow"
	"github.com/korovkin/limiter"
	"github.com/presidium-io/presidium/pkg/cache"
	"github.com/presidium-io/presidium/pkg/cache/redis"
	"github.com/presidium-io/presidium/pkg/service-discovery/consul"
	_ "github.com/presidium-io/presidium/pkg/storage"
)

var (
	storageName   = "ilanastorage" //"ilanastorage"
	storageKey    = ""
	kind          = "azure"
	containerName = "container1"
	grpcPort      = os.Getenv("GRPC_PORT")
)

func main() {
	if grpcPort == "" {
		log.Fatal(fmt.Sprintf("GRPC_PORT (currently [%s]) env var must me set.", grpcPort))
	}

	store := consul.New()
	redisService, err := store.GetService("redis")
	if err != nil {
		log.Fatal(err.Error())
		return
	}

	// projectID := flag.String("project", "", "project id")
	// flag.Parse()
	// logger.Info(fmt.Sprintf("Scanning project %s", *projectID))

	cache := redis.New(
		redisService,
		"", // no password set
		0,  // use default DB
	)

	readFromContainer(&cache)

	// _, err := consul.GetKVPair(*projectID)
	// if err != nil {
	// 	logger.Fatal(fmt.Sprintf("Project not found %s", *projectID))
	// }

}

func readFromContainer(cache *cache.Cache) {
	csf := stow.ConfigMap{"account": storageName, "key": storageKey}
	kind := kind
	location, err := stow.Dial(kind, csf)
	if err != nil {
		log.Fatal(err.Error())
	}

	defer location.Close()

	container, err := location.CreateContainer(containerName)
	if err != nil {
		log.Fatal(err.Error())
	}

	limit := limiter.NewConcurrencyLimiter(10)
	err = stow.Walk(container, stow.CursorStart, 100, func(item stow.Item, err error) error {
		if err != nil {
			return err
		}

		limit.Execute(func() {
			ScanAndAnalyze(cache, container, item)
		})

		return nil
	})
	limit.Wait()

	if err != nil {
		log.Fatal(err.Error())
		return
	}
}
