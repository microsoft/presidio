package storage

import (
	"github.com/presidium-io/presidium/pkg/cache/redis"
	"os"
)

func ExampleCreateAzureConfig() {

	account := os.Getenv("AZURE_STORAGE_ACCOUNT")
	key := os.Getenv("AZURE_STORAGE_KEY")
	container := "files"

	cache := redis.New("localhost:6379", "", 0)

	config, kind := CreateAzureConfig(account, key)
	api, _ := New(cache, config, kind)

	api.ListObjects(container)
	// Output:
	//
}
