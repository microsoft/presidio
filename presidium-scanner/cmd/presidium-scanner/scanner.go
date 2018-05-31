package main

import (
	"bytes"
	"fmt"
	"log"

	"github.com/graymeta/stow"
	"github.com/presidium-io/presidium/pkg/cache"
	_ "github.com/presidium-io/presidium/pkg/storage"
)

// ScanAndAnalyze checks if the file needs to be scanned.
// if it is send it to the analyzer and updates the cache that it was scanned.
func ScanAndAnalyze(cache *cache.Cache, container stow.Container, item stow.Item) {
	var err error
	var val, fileContent, etag string

	// Check if item was scanned in the past (if it's in cache)
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
		fileContent, err = readFileContent(item)
		if err != nil {
			log.Println("ERROR:", err)
			return
		}

		// Replace with a call to analayzer
		fmt.Println(fileContent)

		if err != nil {
			log.Println("ERROR:", err)
			return
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
	// todo: remove printing
	fmt.Println(fileContent)
	err = reader.Close()

	return fileContent, err
}
