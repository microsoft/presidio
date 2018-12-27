package main

import (
	"context"

	types "github.com/Microsoft/presidio-genproto/golang"

	"flag"

	"github.com/spf13/pflag"
	"github.com/spf13/viper"

	log "github.com/Microsoft/presidio/pkg/logger"
	"github.com/Microsoft/presidio/pkg/platform"
	"github.com/Microsoft/presidio/pkg/presidio"
	"github.com/Microsoft/presidio/pkg/presidio/services"
	"github.com/Microsoft/presidio/presidio-collector/cmd/presidio-collector/processor"
	"github.com/Microsoft/presidio/presidio-collector/cmd/presidio-collector/scanner"
	"github.com/Microsoft/presidio/presidio-collector/cmd/presidio-collector/streams"
)

var streamRequest *types.StreamRequest
var scanRequest *types.ScanRequest

func main() {

	pflag.String(platform.AnalyzerSvcAddress, "localhost:3000", "Analyzer service address")
	pflag.String(platform.AnonymizerSvcAddress, "localhost:3001", "Anonymizer service address")
	pflag.String(platform.RedisURL, "localhost:6379", "Redis address")
	pflag.String(platform.RedisPassword, "", "Redis db password (optional)")
	pflag.Int(platform.RedisDb, 0, "Redis db")
	pflag.Bool(platform.RedisSSL, false, "Redis ssl (optional)")
	pflag.String(platform.ScannerRequest, "", "Scanner request")
	pflag.String(platform.StreamRequest, "", "Stream request")
	pflag.String("log_level", "info", "Log level - debug/info/warn/error")

	pflag.CommandLine.AddGoFlagSet(flag.CommandLine)
	pflag.Parse()
	viper.BindPFlags(pflag.CommandLine)

	settings := platform.GetSettings()
	log.CreateLogger(settings.LogLevel)

	parseRequest(settings)

	svc := services.New(settings)
	svc.SetupAnalyzerService()

	if streamRequest.StreamConfig != nil {
		st := streams.CreateStream(context.Background(), streamRequest)
		setupDatasinkService(svc, streamRequest.DatasinkTemplate)
		if streamRequest.AnonymizeTemplate != nil {
			svc.SetupAnonymizerService()
		}

		err := processor.ReceiveEventsFromStream(st, svc, streamRequest)
		if err != nil {
			log.Error(err.Error())
		}
		return
	}

	if scanRequest.ScanTemplate != nil {
		cache := svc.SetupCache()
		setupDatasinkService(svc, scanRequest.DatasinkTemplate)
		if scanRequest.AnonymizeTemplate != nil {
			svc.SetupAnonymizerService()
		}
		scan := scanner.CreateScanner(scanRequest)

		// Scan
		ctx := context.Background()
		err := processor.ScanStorage(ctx, scan, cache, svc, scanRequest)

		if err != nil {
			log.Fatal(err.Error())
		}

		// notify datasink that scanner is done
		svc.CloseDatasink(ctx, &types.CompletionMessage{})
		log.Info("Done!")
	}
}

func setupDatasinkService(svc presidio.ServicesAPI, datasinkTemplate *types.DatasinkTemplate) {
	svc.SetupDatasinkService()

	_, err := svc.InitDatasink(context.Background(), datasinkTemplate)
	if err != nil {
		log.Fatal(err.Error())
	}
}

func parseRequest(settings *platform.Settings) {

	streamRequest = &types.StreamRequest{}
	presidio.ConvertJSONToInterface(settings.StreamRequest, streamRequest)
	if streamRequest.StreamConfig != nil {
		return
	}
	scanRequest = &types.ScanRequest{}
	presidio.ConvertJSONToInterface(settings.ScannerRequest, scanRequest)

}
