package main

import (
	"bytes"
	"context"
	"fmt"
	"path/filepath"

	message_types "github.com/presid-io/presidio-genproto/golang"
	c "github.com/presid-io/presidio/pkg/cache"
	"github.com/presid-io/presidio/pkg/modules/analyzer"
	"github.com/presid-io/stow"
)

// ScanAndAnalyze checks if the file needs to be scanned.
// Then sends it to the analyzer and updates the cache that it was scanned.
func ScanAndAnalyze(cache *c.Cache, item stow.Item,
	analyzerModule *analyzer.Analyzer,
	analyzeRequest *message_types.AnalyzeRequest) ([]*message_types.AnalyzeResult, error) {
	var err error
	var val, fileContent, etag string

	// Check if file type supported
	ext := filepath.Ext(item.Name())

	if ext != ".txt" && ext != ".csv" && ext != ".json" && ext != ".tsv" {
		return nil, fmt.Errorf("Expected: file extension txt, csv, json, tsv, received: %s", ext)
	}

	// Check if the item was scanned in the past (if it's in the cache)
	etag, err = item.ETag()
	if err != nil {
		return nil, err
	}

	val, err = (*cache).Get(etag)
	if err != nil {
		return nil, err
	}

	// Value not found in the cache. Need to scan the file and update the cache
	if val == "" {
		fileContent, err = readFileContent(item)
		if err != nil {
			return nil, err
		}

		results, err := (*analyzerModule).InvokeAnalyze(context.Background(), analyzeRequest, fileContent)
		if err != nil {
			return nil, err
		}

		return results.AnalyzeResults, nil
	}

	// Otherwise skip- item was already scanned
	return nil, nil
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
