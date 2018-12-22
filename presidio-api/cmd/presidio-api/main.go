package main

import (
	"os"
	"strconv"

	"github.com/spf13/pflag"
	"github.com/spf13/viper"

	log "github.com/Microsoft/presidio/pkg/logger"
	"github.com/Microsoft/presidio/pkg/platform"
	"github.com/Microsoft/presidio/pkg/platform/kube"
	"github.com/Microsoft/presidio/pkg/platform/local"
	server "github.com/Microsoft/presidio/pkg/server"
)

func main() {

	pflag.Int("web_port", 8080, "HTTP listen port")
	pflag.String("analyzer_svc_address", "localhost:3000", "Analyzer service address")
	pflag.String("anonymizer_svc_address", "localhost:3001", "Anonymizer service address")
	pflag.String("redis_url", "", "Redis address")

	pflag.Parse()
	viper.BindPFlags(pflag.CommandLine)

	settings := platform.GetSettings()

	port, err := strconv.Atoi(settings.WebPort)
	if err != nil {
		log.Fatal(err.Error())
	}

	var api *API

	// Kubernetes platform
	if settings.Namespace != "" {
		store, err := kube.New(settings.Namespace, "")
		if err != nil {
			log.Fatal(err.Error())
		}
		api = New(store)
	} else {
		// Local platform
		store, err := local.New(os.TempDir())
		if err != nil {
			log.Fatal(err.Error())
		}
		api = New(store)
	}

	api.setupGRPCServices()
	setupHTTPServer(api, port)
}

func setupHTTPServer(api *API, port int) {

	r := server.Setup(port)

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
				action.GET(":id", api.getActionTemplate)
				// POST template
				action.POST(":id", api.postActionTemplate)
				// PUT, update template
				action.PUT(":id", api.putActionTemplate)
				// DELETE template
				action.DELETE(":id", api.deleteActionTemplate)
			}
		}

		// Actions group
		projects := v1.Group("projects/:project")
		{
			// Analyze text
			// /api/v1/projects/123/analyze
			projects.POST("/analyze", api.analyze)

			// Anonymize text
			// /api/v1/projects/123/anonymize
			projects.POST("/anonymize", api.anonymize)

			// Schedule scanning cron job
			// /api/v1/projects/123/schedule-scanner-cronjob
			projects.POST("/schedule-scanner-cronjob", api.scheduleScannerCronJob)

			// Schedule streams job
			// /api/v1/projects/123/schedule-streams-job
			projects.POST("/schedule-streams-job", api.scheduleStreamsJob)

		}

	}
	server.Start(r)
}
