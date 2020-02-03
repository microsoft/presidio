package main

import (
	"flag"
	"os"

	"github.com/spf13/pflag"
	"github.com/spf13/viper"

	"github.com/Microsoft/presidio/pkg/cache"
	log "github.com/Microsoft/presidio/pkg/logger"
	"github.com/Microsoft/presidio/pkg/platform"
	"github.com/Microsoft/presidio/pkg/platform/kube"
	"github.com/Microsoft/presidio/pkg/platform/local"

	"github.com/Microsoft/presidio/pkg/presidio/services"
	server "github.com/Microsoft/presidio/pkg/server"
	store "github.com/Microsoft/presidio/presidio-api/cmd/presidio-api/api"

	// This line is necessary for go-swagger to find the docs!
	_ "github.com/Microsoft/presidio/presidio-api/cmd/presidio-api/docs"
)

var api *store.API

func main() {

	pflag.Int(platform.WebPort, 8080, "HTTP listen port")
	pflag.String(platform.AnalyzerSvcAddress, "localhost:3000", "Analyzer service address")
	pflag.String(platform.AnonymizerSvcAddress, "localhost:3001", "Anonymizer service address")
	pflag.String(platform.AnonymizerImageSvcAddress, "", "Anonymizer image service address (optional)")
	pflag.String(platform.OcrSvcAddress, "", "ocr service address (optional)")
	pflag.String(platform.SchedulerSvcAddress, "", "Scheduler service address (optional)")
	pflag.String(platform.RecognizersStoreSvcAddress, "localhost:3004", "Recognizers store service address")
	pflag.String(platform.RedisURL, "", "Redis address (optional)")
	pflag.String(platform.RedisPassword, "", "Redis db password (optional)")
	pflag.Int(platform.RedisDb, 0, "Redis db (optional)")
	pflag.Bool(platform.RedisSSL, false, "Redis ssl (optional)")
	pflag.String(platform.PresidioNamespace, "", "Presidio Kubernetes namespace (optional)")
	pflag.String("log_level", "info", "Log level - debug/info/warn/error")

	pflag.CommandLine.AddGoFlagSet(flag.CommandLine)
	pflag.Parse()
	viper.BindPFlags(pflag.CommandLine)

	settings := platform.GetSettings()
	log.CreateLogger(settings.LogLevel)

	svc := services.New(settings)

	// Setup Redis cache

	var cacheStore cache.Cache

	if settings.RedisURL != "" {
		cacheStore = svc.SetupCache()
	}

	// Kubernetes platform
	if settings.Namespace != "" {
		platformStore, err := kube.New(settings.Namespace, "")
		if err != nil {
			log.Fatal(err.Error())
		}
		api = store.New(platformStore, cacheStore, settings)
	} else {
		// Local platform
		platformStore, err := local.New(os.TempDir())
		if err != nil {
			log.Fatal(err.Error())
		}
		api = store.New(platformStore, cacheStore, settings)
	}

	api.SetupGRPCServices()
	setupHTTPServer(settings.WebPort, settings.LogLevel)
}

// Note:
// 	 When modifying the API: Like adding or removing end-points, updating parameters, or updating responses,
// 	 remember to make the relevant modifications in the files under the /docs package, and then re-generate
// 	 the /docs/swagger.yaml according to the /docs/readme.md instructions.

func setupHTTPServer(port int, loglevel string) {

	r := server.Setup(port, loglevel)

	// api/v1 group
	v1 := r.Group("/api/v1")
	{
		// GET available field types
		v1.GET("fieldTypes", getFieldTypes)

		// templates group
		templates := v1.Group("/templates/:project")
		{
			// /api/v1/templates/123/analyze/1234
			// /api/v1/templates/123/anonymize/1234
			action := templates.Group("/:action")
			{
				// GET template
				action.GET(":id", getActionTemplate)
				// POST template
				action.POST(":id", postActionTemplate)
				// PUT, update template
				action.PUT(":id", putActionTemplate)
				// DELETE template
				action.DELETE(":id", deleteActionTemplate)
			}
		}

		// Actions group
		projects := v1.Group("projects/:project")
		{
			// Analyze text
			// /api/v1/projects/123/analyze
			projects.POST("/analyze", analyzeText)

			// Anonymize text
			// /api/v1/projects/123/anonymize
			projects.POST("/anonymize", anonymizeText)

			// Anonymize image
			// /api/v1/projects/123/anonymize-image
			projects.POST("/anonymize-image", anonymizeImage)

			// Schedule scanning cron job
			// /api/v1/projects/123/schedule-scanner-cronjob
			projects.POST("/schedule-scanner-cronjob", scheduleScannerCronJob)

			// Schedule streams job
			// /api/v1/projects/123/schedule-streams-job
			projects.POST("/schedule-streams-job", scheduleStreamJob)
		}

		// recognizers group
		// /api/v1/analyzer/recognizers
		recognizers := v1.Group("/analyzer/recognizers")
		{
			// Get an existing recognizer
			recognizers.GET(":id", getRecognizer)

			// Get all existing recognizers
			recognizers.GET("/", getAllRecognizers)

			// Insert a new recognizer
			recognizers.POST(":id", insertRecognizer)

			// Update an existing recognizer
			recognizers.PUT(":id", updateRecognizer)

			// DELETE a recognizer
			recognizers.DELETE(":id", deleteRecognizer)
		}
	}
	server.Start(r)
}
