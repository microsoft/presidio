package main

import (
	"log"
	"sync"

	"github.com/graymeta/stow"
	"github.com/presidium-io/presidium/pkg/cache"
	"github.com/presidium-io/presidium/pkg/cache/redis"
	"github.com/presidium-io/presidium/pkg/service-discovery/consul"
	_ "github.com/presidium-io/presidium/pkg/storage"
)

type redisItem struct {
	Name string
	ETag string
}

func main() {
	store := consul.New()
	redisService, err := store.GetService("redis")
	if err != nil {
		log.Fatal(err.Error())
		return
	}

	// projectID := flag.String("project", "", "project id")
	// flag.Parse()
	// logger.Info(fmt.Sprintf("Scanning project %s", *projectID))

	redisCache := redis.New(
		redisService,
		"", // no password set
		0,  // use default DB
	)

	readFromContainer(&redisCache)

	// _, err := consul.GetKVPair(*projectID)
	// if err != nil {
	// 	logger.Fatal(fmt.Sprintf("Project not found %s", *projectID))
	// }

}

func readFromContainer(redisCache *cache.Cache) {
	//csf := stow.ConfigMap{"account": "ilanastorage", "key": ""}
	csf := stow.ConfigMap{"account": "presidiumtests", "key": ""}
	kind := "azure"
	location, err := stow.Dial(kind, csf)
	if err != nil {
		log.Fatal(err.Error())
		return
	}

	//containers := make([]stow.Container, 1)
	err = stow.WalkContainers(location, stow.NoPrefix, 100, func(c stow.Container, err error) error {
		if err != nil {
			return err
		}

		var wg sync.WaitGroup
		err = stow.Walk(c, stow.CursorStart, 100, func(item stow.Item, err error) error {
			wg.Add(1)
			if err != nil {
				return err
			}

			go ScanAndAnalyaze(redisCache, c, item, &wg)
			return nil
		})
		wg.Wait()

		return err
	})
	if err != nil {
		log.Fatal(err.Error())
		return
	}
}
