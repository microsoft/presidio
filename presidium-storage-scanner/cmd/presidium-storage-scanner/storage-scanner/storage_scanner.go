package storageScanner

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"log"
	"path/filepath"

	"github.com/presidium-io/stow"

	message_types "github.com/presidium-io/presidium-genproto/golang"
	"github.com/presidium-io/presidium/pkg/cache"
	analyzer "github.com/presidium-io/presidium/pkg/modules/analyzer"
)

type scanResult struct {
	Field        string
	Probability  float32
	FileName     string
	ConainerName string
}

// ScanAndAnalyze checks if the file needs to be scanned.
// Then sends it to the analyzer and updates the cache that it was scanned.
func ScanAndAnalyze(cache *cache.Cache, container stow.Container, item stow.Item,
	analyzerModule *analyzer.Analyzer,
	analyzeRequest *message_types.AnalyzeRequest) []byte {
	var err error
	var val, fileContent, etag string

	// Check if file type supported
	ext := filepath.Ext(item.Name())

	if ext != ".txt" && ext != ".csv" && ext != ".json" && ext != ".tsv" {
		log.Println("Expected: file extension txt, csv, json, tsv, received:", ext)
		return nil
	}

	// Check if the item was scanned in the past (if it's in cache)
	etag, err = item.ETag()
	if err != nil {
		log.Println("ERROR:", err)
		return nil
	}

	val, err = (*cache).Get(etag)
	if err != nil {
		log.Println("ERROR:", err)
		return nil
	}

	// Value not found in the cache. Need to scan the file and update the cache
	if val == "" {
		log.Println("empty cache for file:", item.Name())
		fileContent, err = readFileContent(item)
		if err != nil {
			log.Println("ERROR:", err)
			return nil
		}
		log.Println(fileContent)

		results, err := (*analyzerModule).InvokeAnalyze(context.Background(), analyzeRequest, fileContent)
		if err != nil {
			log.Println("ERROR:", err)
			return nil
		}

		var scanResults []scanResult
		for _, r := range results.AnalyzeResults {
			sResult := scanResult{
				r.Field.String(), r.Probability, item.Name(), container.Name(),
			}
			scanResults = append(scanResults, sResult)

			log.Println(fmt.Sprintf("Found: %q, propability: %f, Location: start:%d end:%d length:%d",
				r.Field, r.Probability, r.Location.Start, r.Location.End, r.Location.Length))
		}
		scanResultsByteArray, err := json.Marshal(scanResults)
		if err != nil {
			log.Fatal("Cannot encode to JSON ", err)
			return nil
		}

		err = (*cache).Set(etag, item.Name())
		if err != nil {
			log.Println("ERROR:", err)
		}

		return scanResultsByteArray
	}

	// Otherwise skip- item was already scanned
	log.Println("Item was already scanned", item.Name())
	return nil
}

// Read the content of the cloud item
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
