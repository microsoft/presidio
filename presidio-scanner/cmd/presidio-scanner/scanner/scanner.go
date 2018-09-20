package scanner

import (
	"context"
	"fmt"

	types "github.com/Microsoft/presidio-genproto/golang"
	"github.com/Microsoft/presidio/pkg/cache"
	log "github.com/Microsoft/presidio/pkg/logger"
)

// ScanFunc is the function the is executed on the scanned item
type ScanFunc func(item interface{}) error

// Scanner interface represent the supported scanner methods.
type Scanner interface {
	//Init the scanner
	Init(inputConfig *types.CloudStorageConfig)

	//Scan walks over the items to scan and executes ScanFunc on each of the items
	Scan(fn ScanFunc) error
}

//ScanData the data
func ScanData(scanner Scanner, scanRequest *types.ScanRequest, cache cache.Cache,
	analyzeService *types.AnalyzeServiceClient, analyzeRequest *types.AnalyzeRequest,
	anonymizeService *types.AnonymizeServiceClient, datasinkService *types.DatasinkServiceClient) error {

	return scanner.Scan(func(item interface{}) error {
		var analyzerResult []*types.AnalyzeResult
		var text string

		scanItem := CreateItem(scanRequest, item)
		itemPath := scanItem.GetPath()
		uniqueID, err := scanItem.GetUniqueID()
		if err != nil {
			return err
		}

		shouldScan, err := shouldScanItem(&cache, scanItem, uniqueID)
		if err != nil {
			return err
		}

		if shouldScan {
			text, analyzerResult, err = analyzeItem(analyzeService, analyzeRequest, scanItem)
			if err != nil {
				return err
			}

			if len(analyzerResult) > 0 {
				anonymizerResult, err := anonymizeItem(analyzerResult, text, itemPath, scanRequest.AnonymizeTemplate, anonymizeService)
				if err != nil {
					return err
				}

				err = sendResultToDatasink(itemPath, analyzerResult, anonymizerResult, cache, datasinkService)
				if err != nil {
					return err
				}
				log.Info("%d results were sent to the datasink successfully", len(analyzerResult))

			}
			writeItemToCache(uniqueID, itemPath, cache)
			return nil
		}

		log.Info("item %s was already scanned", itemPath)
		return nil
	})
}

func anonymizeItem(analyzeResults []*types.AnalyzeResult, text string, path string, anonymizeTemplate *types.AnonymizeTemplate,
	anonymizeService *types.AnonymizeServiceClient) (*types.AnonymizeResponse, error) {
	if anonymizeTemplate != nil {
		srv := *anonymizeService

		anonymizeRequest := &types.AnonymizeRequest{
			Template:       anonymizeTemplate,
			Text:           text,
			AnalyzeResults: analyzeResults,
		}
		res, err := srv.Apply(context.Background(), anonymizeRequest)
		return res, err
	}
	return nil, nil
}

func writeItemToCache(uniqueID string, scannedPath string, cache cache.Cache) {
	// If writing to datasink succeeded - update the cache
	err := cache.Set(uniqueID, scannedPath)
	if err != nil {
		log.Error(err.Error())
	}
}

func sendResultToDatasink(scannedPath string, analyzeResults []*types.AnalyzeResult,
	anonymizeResults *types.AnonymizeResponse, cache cache.Cache,
	datasinkService *types.DatasinkServiceClient) error {
	srv := *datasinkService

	for _, element := range analyzeResults {
		// Remove PII from results
		element.Text = ""
	}

	datasinkRequest := &types.DatasinkRequest{
		AnalyzeResults:  analyzeResults,
		AnonymizeResult: anonymizeResults,
		Path:            scannedPath,
	}

	_, err := srv.Apply(context.Background(), datasinkRequest)
	return err
}

// Sends analyzer scan request to the analyzer service and returns analyzer result
func analyzeItem(
	analyzeService *types.AnalyzeServiceClient,
	analyzeRequest *types.AnalyzeRequest,
	item Item) (string, []*types.AnalyzeResult, error) {

	// Value not found in the cache. Need to scan the file and update the cache
	itemContent, err := item.GetContent()
	if err != nil {
		return "", nil, fmt.Errorf("error getting item's content, error: %q", err.Error())
	}

	analyzeRequest.Text = itemContent

	srv := *analyzeService
	results, err := srv.Apply(context.Background(), analyzeRequest)
	if err != nil {
		return "", nil, err
	}

	return itemContent, results.AnalyzeResults, nil
}

func shouldScanItem(cache *cache.Cache, item Item, uniqueID string) (bool, error) {
	err := item.IsContentTypeSupported()
	if err != nil {
		return false, err
	}

	val, err := (*cache).Get(uniqueID)
	if err != nil {
		return false, err
	}

	// if value is not in cache, cache.get will return ""
	shouldScan := val == ""
	return shouldScan, nil
}
