package main

import (
	"context"
	"fmt"
	"os"
	"strings"

	log "github.com/presid-io/presidio/pkg/logger"

	"google.golang.org/grpc/reflection"

	message_types "github.com/presid-io/presidio-genproto/golang"
	"github.com/presid-io/presidio/pkg/rpc"
	"github.com/presid-io/presidio/presidio-databinder/cmd/presidio-databinder/databinder"
)

var (
	grpcPort        = os.Getenv("GRPC_PORT")
	databinderArray []*databinder.DataBinder
)

type server struct{}

func main() {
	if grpcPort == "" {
		// Set to default
		grpcPort = "5000"
	}

	// Setup server
	lis, s := rpc.SetupClient(grpcPort)

	message_types.RegisterDatabinderServiceServer(s, &server{})
	reflection.Register(s)

	// Listen for client requests
	if err := s.Serve(lis); err != nil {
		log.Fatal(err.Error())
	}
}

func (s *server) Init(ctx context.Context, databinderTemplate *message_types.DatabinderTemplate) (*message_types.DatabinderResponse, error) {
	if databinderTemplate == nil || databinderTemplate.Databinder == nil {
		return &message_types.DatabinderResponse{}, fmt.Errorf("databinderTemplate must me set")
	}

	// initialize each of the databinders
	for _, databinder := range databinderTemplate.Databinder {
		if databinder.GetBindType() == "" {
			return &message_types.DatabinderResponse{}, fmt.Errorf("bindType var must me set")
		}
		if databinder.GetConnectionString() == "" {
			return &message_types.DatabinderResponse{}, fmt.Errorf("connectionString var must me set")
		}

		createDatabiner(databinder.GetBindType(), databinder.GetConnectionString(), databinder.GetTableName())
	}

	return &message_types.DatabinderResponse{}, nil
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
	return target == message_types.DataBinderTypesEnum.String(message_types.DataBinderTypesEnum_mssql) ||
		target == message_types.DataBinderTypesEnum.String(message_types.DataBinderTypesEnum_mysql) ||
		target == message_types.DataBinderTypesEnum.String(message_types.DataBinderTypesEnum_oracle) ||
		target == message_types.DataBinderTypesEnum.String(message_types.DataBinderTypesEnum_oracle) ||
		target == message_types.DataBinderTypesEnum.String(message_types.DataBinderTypesEnum_postgres) ||
		target == message_types.DataBinderTypesEnum.String(message_types.DataBinderTypesEnum_sqlite3)
}
