package main

import (
	"os"
	"strconv"

	log "github.com/presid-io/presidio/pkg/logger"
	"github.com/presid-io/presidio/pkg/platform/kube"
	"github.com/presid-io/presidio/pkg/platform/local"

	server "github.com/presid-io/presidio/pkg/server"
)

var (
	webPort   = os.Getenv("WEB_PORT")
	namespace = os.Getenv("presidio_NAMESPACE")
)

func main() {

	if webPort == "" {
		log.Fatal("WEB_PORT env var must me set.")
	}

	port, err := strconv.Atoi(webPort)
	if err != nil {
		log.Fatal(err.Error())
	}

	r := server.Setup(port)
	setupGrpcServices()

	var api *API

	// Kubernetes platform
	if namespace != "" {
		store, err := kube.New(namespace)
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
		}

	}
	server.Start(r)
}
