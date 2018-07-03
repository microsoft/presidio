package storageScanner

import (
	"bytes"
	"context"
	"fmt"
	"log"

	"github.com/presidium-io/stow"

	"github.com/presidium-io/presidium/pkg/cache"
	request "github.com/presidium-io/presidium/pkg/request"
	message_types "github.com/presidium-io/presidium/pkg/types"
)

// ScanAndAnalyze checks if the file needs to be scanned.
// Then sends it to the analyzer and updates the cache that it was scanned.
func ScanAndAnalyze(cache *cache.Cache, container stow.Container, item stow.Item, analyzeService *message_types.AnalyzeServiceClient,
	analyzeRequest *message_types.AnalyzeRequest) {
	var err error
	var val, fileContent, etag string

	// Check if the item was scanned in the past (if it's in cache)
	etag, err = item.ETag()
	if err != nil {
		log.Println("ERROR:", err)
		return
	}

	val, err = (*cache).Get(etag)
	if err != nil {
		log.Println("ERROR:", err)
		return
	}

	// Value not found in the cache. Need to scan the file and update the cache
	if val == "" {
		log.Println("empty cache for file:", item.Name())
		fileContent, err = readFileContent(item)
		if err != nil {
			log.Println("ERROR:", err)
			return
		}
		log.Println(fileContent)

		results, err := request.InvokeAnalyze(context.Background(), analyzeService, analyzeRequest, fileContent)
		if err != nil {
			log.Println("ERROR:", err)
			return
		}

		for _, r := range results.Results {
			log.Println(fmt.Sprintf("Found: %q, propability: %f, Location: start:%d end:%d length:%d",
				r.FieldType, r.Probability, r.Location.Start, r.Location.End, r.Location.Length))
		}

		err = (*cache).Set(etag, item.Name())
		if err != nil {
			log.Println("ERROR:", err)
		}
		return
	}

	// Otherwise skip- item was already scanned
	log.Println("Item was already scanned", item.Name())
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
	err = reader.Close()

	return fileContent, err
}
