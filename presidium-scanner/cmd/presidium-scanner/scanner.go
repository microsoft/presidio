package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"log"
	"sync"

	"github.com/graymeta/stow"
	"github.com/presidium-io/presidium/pkg/cache"
	_ "github.com/presidium-io/presidium/pkg/storage"
)

// ScanAndAnalyaze checks if the file needs to be scanned.
// if it is send it to the analyzer and updates the Redis cache that it was scanned.
func ScanAndAnalyaze(redisCache *cache.Cache, container stow.Container, item stow.Item, wg *sync.WaitGroup) {
	defer wg.Done()

	// Check if item was scanned in the past (if it's in Redis)
	filePath := getFilePath(container.Name(), item.Name())
	val, err := (*redisCache).Get(filePath)

	if err != nil {
		log.Fatal(err.Error())
		return
	}

	// Value not found in redis. Need to scan the file and update Redis
	if val == "" {
		fileContent, error := readFileContent(item)
		if error != nil {
			log.Fatal(error.Error())
			return
		}

		// Replace with a call to analayzer
		fmt.Println(fileContent)

		etag, error := item.ETag()
		if error != nil {
			log.Fatal(error.Error())
			return
		}

		ri := &redisItem{
			ETag: etag,
			Name: item.Name(),
		}

		error = writeItemToRedis(redisCache, ri, filePath)
		if error != nil {
			log.Fatal(error.Error())
		}
		return
	}

	// value was found in Redis, validate that the Etags are equal - which means that the file was already scanned
	ri := redisItem{}

	if err = json.Unmarshal([]byte(val), &ri); err != nil {
		log.Fatal(err.Error())
		return
	}

	fmt.Println(ri)
	etag, err := item.ETag()

	if err != nil {
		log.Fatal(err.Error())
		return
	}

	if etag != ri.ETag {
		// file was changed, scan again and update redis
		ri.ETag = etag
		err = writeItemToRedis(redisCache, &ri, filePath)
		log.Fatal(err.Error())
	}
}

// file path is structure is: containerName/fileName
func getFilePath(container string, file string) string {
	var buffer bytes.Buffer
	buffer.WriteString(container)
	buffer.WriteString("/")
	buffer.WriteString(file)
	return buffer.String()
}

// Read the content of the cloud item
// TODO: Validate it's a text file
func readFileContent(item stow.Item) (string, error) {
	reader, err := item.Open()

	if err != nil {
		return "", err
	}

	buf := new(bytes.Buffer)

	if _, err = buf.ReadFrom(reader); err != nil {
		return "", err
	}

	fileContent := buf.String()
	// todo: remove printing
	fmt.Println(fileContent)
	err = reader.Close()

	return fileContent, err
}

func writeItemToRedis(redisCache *cache.Cache, ri *redisItem, filePath string) error {
	byteArr, error := json.Marshal(ri)
	if error != nil {
		return error
	}

	error = (*redisCache).Set(filePath, string(byteArr))
	return error
}
