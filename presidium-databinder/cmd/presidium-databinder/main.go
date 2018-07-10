package main

import (
	"context"
	"fmt"
	"os"
	"strings"

	log "github.com/presidium-io/presidium/pkg/logger"
	"github.com/presidium-io/presidium/pkg/templates"

	"github.com/joho/godotenv"
	_ "github.com/lib/pq"
	"google.golang.org/grpc/reflection"

	message_types "github.com/presidium-io/presidium-genproto/golang"
	"github.com/presidium-io/presidium/pkg/kv/consul"
	"github.com/presidium-io/presidium/pkg/rpc"
)

type databinder struct {
	Name                   string
	ConnectionStringK8sKey string
}

var (
	grpcPort         = os.Getenv("GRPC_PORT")
	driverName       string
	connectionString string
	template         *templates.Templates
	databinderArray  []databinder
)

type server struct{}

func main() {
	// Setup server
	lis, s := rpc.SetupClient(grpcPort)

	message_types.RegisterDatabinderServiceServer(s, &server{})
	reflection.Register(s)
	template = templates.New(consul.New())

	// Get template key from env variable(???)
	key := "???"

	// Load template from consul
	template.GetTemplate(key)

	// databinderRequest := &message_types.AnalyzeRequest{}
	// err = helper.ConvertJSONToInterface(template, analyzeRequest)

	// foreach databinder -  init DB
	initDatabase()
	databinderArray = append(databinderArray, databinder{Name: "mysql", ConnectionStringK8sKey: ""})

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

	// TODO: Remove!!
	driverName = os.Getenv("DRIVER_NAME")
	connectionString = os.Getenv("DB_CONNECTION_STRING")

	if driverName == "" {
		log.Fatal("DRIVER_NAME env var must me set")
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
		if isDatabase(element.Name) {
			err := writeResultsToDB(r.AnalyzeResults, r.Path)
			if err != nil {
				errstrings = append(errstrings, err.Error())
			}
		}
		// TODO: Add other outputs support
	}

	return nil, fmt.Errorf(strings.Join(errstrings, "\n"))
}

func isDatabase(target string) bool {
	return target == "mysql" || target == "mssql" || target == "oracle" || target == "postgres"
}
