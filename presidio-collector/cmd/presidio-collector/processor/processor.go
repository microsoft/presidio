package processor

import (
	"context"
	"fmt"

	types "github.com/microsoft/presidio-genproto/golang"

	"github.com/microsoft/presidio/pkg/cache"
	"github.com/microsoft/presidio/pkg/presidio"
	"github.com/microsoft/presidio/pkg/stream"

	log "github.com/microsoft/presidio/pkg/logger"
	"github.com/microsoft/presidio/presidio-collector/cmd/presidio-collector/scanner"
)

//ReceiveEventsFromStream ..
func ReceiveEventsFromStream(st stream.Stream, services presidio.ServicesAPI, streamRequest *types.StreamRequest) error {
	return st.Receive(func(ctx context.Context, partition string, sequence string, text string) error {

		analyzerResult, err := services.AnalyzeItem(ctx, text, streamRequest.AnalyzeTemplate)
		if err != nil {
			err = fmt.Errorf("error analyzing message: %s, error: %q", text, err.Error())
			return err
		}

		if len(analyzerResult) > 0 {
			anonymizerResult, err := services.AnonymizeItem(ctx, analyzerResult, text, streamRequest.AnonymizeTemplate)

			if err != nil {
				err = fmt.Errorf("error anonymizing item: %s/%s, error: %q", partition, sequence, err.Error())
				return err
			}

			err = services.SendResultToDatasink(ctx, analyzerResult, anonymizerResult, fmt.Sprintf("%s/%s", partition, sequence))
			if err != nil {
				err = fmt.Errorf("error sending message to datasink: %s/%s, error: %q", partition, sequence, err.Error())
				return err
			}
			log.Debug("%d results were sent to the datasink successfully", len(analyzerResult))

		}
		return nil
	})
}

//ScanStorage ..
func ScanStorage(ctx context.Context, scan scanner.Scanner, cache cache.Cache, services presidio.ServicesAPI, scanRequest *types.ScanRequest) error {
	return scan.Scan(func(item interface{}) error {
		var analyzerResult []*types.AnalyzeResult

		scanItem := scanner.CreateItem(scanRequest, item)
		itemPath := scanItem.GetPath()
		uniqueID, err := scanItem.GetUniqueID()
		if err != nil {
			return err
		}

		err = scanItem.IsContentTypeSupported()
		if err != nil {
			return err
		}

		shouldScan, err := isItemInCache(cache, uniqueID)
		if err != nil {
			return err
		}

		if shouldScan {

			// Value not found in the cache. Need to scan the file and update the cache
			content, err := scanItem.GetContent()
			if err != nil {
				return fmt.Errorf("error getting item's content, error: %q", err.Error())
			}

			analyzerResult, err = services.AnalyzeItem(ctx, content, scanRequest.AnalyzeTemplate)
			if err != nil {
				return err
			}
			log.Debug("analyzed %d results", len(analyzerResult))

			if len(analyzerResult) > 0 {
				anonymizerResult, err := services.AnonymizeItem(ctx, analyzerResult, content, scanRequest.AnonymizeTemplate)
				if err != nil {
					return err
				}

				err = services.SendResultToDatasink(ctx, analyzerResult, anonymizerResult, itemPath)
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

func isItemInCache(cache cache.Cache, key string) (bool, error) {

	val, err := cache.Get(key)
	if err != nil {
		return false, err
	}

	// if value is not in cache, cache.get will return ""
	exist := val == ""
	return exist, nil
}

func writeItemToCache(key string, value string, cache cache.Cache) {
	// If writing to datasink succeeded - update the cache
	err := cache.Set(key, value)
	if err != nil {
		log.Error(err.Error())
	}
}
