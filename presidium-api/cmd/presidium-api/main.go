package main

import (
	"fmt"
	"os"
	"strconv"

	"github.com/presidium-io/presidium/pkg/kv/consul"
	log "github.com/presidium-io/presidium/pkg/logger"
	server "github.com/presidium-io/presidium/pkg/server"
)

var (
	webPort           = os.Getenv("WEB_PORT")
	analyzerSvcHost   = os.Getenv("ANALYZER_SVC_HOST")
	anonymizerSvcHost = os.Getenv("ANONYMIZER_SVC_HOST")
)

func main() {

	if webPort == "" || analyzerSvcHost == "" || anonymizerSvcHost == "" {
		log.Fatal(fmt.Sprintf("WEB_PORT (currently [%s]) ANALYZER_SVC_HOST (currently [%s]) and ANONYMIZER_SVC_HOST (currently [%s]) env vars must me set.", webPort, analyzerSvcHost, anonymizerSvcHost))
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
				action.PATCH(":id", api.patchActionTemplate)
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
