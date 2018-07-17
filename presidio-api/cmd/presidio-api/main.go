package main

import (
	"os"
	"strconv"

	"github.com/presid-io/presidio/pkg/kv/consul"
	log "github.com/presid-io/presidio/pkg/logger"
	server "github.com/presid-io/presidio/pkg/server"
)

var (
	webPort = os.Getenv("WEB_PORT")
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

	api := New(consul.New())
	v1 := r.Group("/api/v1")
	{
		v1.GET("fieldTypes", getFieldTypes)

		templates := v1.Group("/templates/:project")
		{
			// /api/v1/templates/123/analyze/1234
			// /api/v1/templates/123/anonymize/1234
			action := templates.Group("/:action")
			{
				action.GET(":id", api.getActionTemplate)
				action.POST(":id", api.postActionTemplate)
				action.PATCH(":id", api.putActionTemplate)
				action.DELETE(":id", api.deleteActionTemplate)
			}
		}

		projects := v1.Group("projects/:project")
		{
			// /api/v1/projects/123/analyze
			projects.POST("/analyze", api.analyze)

			// /api/v1/projects/123/anonymize
			projects.POST("/anonymize", api.anonymize)
		}

	}
	server.Start(r)
}
