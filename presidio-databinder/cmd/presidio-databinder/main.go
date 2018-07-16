package main

import (
	"context"
	"fmt"
	"os"
	"strings"

	log "github.com/presid-io/presidio/pkg/logger"
	"github.com/presid-io/presidio/pkg/templates"

	"github.com/joho/godotenv"
	"google.golang.org/grpc/reflection"

	message_types "github.com/presid-io/presidio-genproto/golang"
	"github.com/presid-io/presidio/pkg/kv/consul"
	"github.com/presid-io/presidio/pkg/modules/databinder"
	"github.com/presid-io/presidio/pkg/rpc"
	"github.com/presid-io/presidio/presidio-databinder/cmd/presidio-databinder/database"
)

var (
	grpcPort         = os.Getenv("GRPC_PORT")
	bindType         string
	connectionString string
	template         *templates.Templates
	databinderArray  []*databinder.DataBinder
)

type server struct{}

func main() {
	// Setup server
	lis, s := rpc.SetupClient(grpcPort)

	message_types.RegisterDatabinderServiceServer(s, &server{})
	reflection.Register(s)
	template = templates.New(consul.New())

	// Get template key from env variable(???)
	// key := "???"

	// // Load template from consul
	// t, err = template.GetTemplate(key)

	// databinderRequest := &message_types.AnalyzeRequest{}
	// err = helper.ConvertJSONToInterface(template, analyzeRequest)

	// foreach databinder -  init databinder

	// TEMP VALUES!!!

	if isDatabase(bindType) {
		dbwritter := databaseBinder.New(bindType, connectionString)
		databinderArray = append(databinderArray, &dbwritter)
	}

	// Listen for client requests
	if err := s.Serve(lis); err != nil {
		log.Fatal(err.Error())
	}
}

func init() {
	err := godotenv.Load()
	if err != nil {
		log.Fatal("Error loading .env file")
	}

	bindType = os.Getenv("BIND_TYPE")
	connectionString = os.Getenv("DB_CONNECTION_STRING")

	if bindType == "" {
		log.Fatal("BIND_TYPE env var must me set")
	}

	if connectionString == "" {
		log.Fatal("DB_CONNECTION_STRING env var must me set")
	}

	if grpcPort == "" {
		// Set to default
		grpcPort = "5000"
	}
}

func (s *server) Apply(ctx context.Context, r *message_types.DatabinderRequest) (*message_types.DatabinderResponse, error) {
	// create a slice for the errors
	var errstrings []string

	for _, element := range databinderArray {
		err := (*element).WriteResults(r.AnalyzeResults, r.Path)
		if err != nil {
			errstrings = append(errstrings, err.Error())
		}
	}

	var combinedError error
	if len(errstrings) > 0 {
		combinedError = fmt.Errorf(strings.Join(errstrings, "\n"))
	}
	return &message_types.DatabinderResponse{}, combinedError
}

func isDatabase(target string) bool {
	return target == "mysql" || target == "mssql" || target == "oracle" || target == "postgres"
}
