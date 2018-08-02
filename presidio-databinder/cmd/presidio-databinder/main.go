package main

import (
	"context"
	"fmt"
	"os"
	"strings"

	log "github.com/Microsoft/presidio/pkg/logger"

	"google.golang.org/grpc/reflection"

	message_types "github.com/Microsoft/presidio-genproto/golang"
	"github.com/Microsoft/presidio/pkg/rpc"
	"github.com/Microsoft/presidio/presidio-databinder/cmd/presidio-databinder/databinder"
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

	var err error
	// initialize each of the databinders
	for _, databinder := range databinderTemplate.Databinder {
		if databinder.GetBindType() == "" {
			return &message_types.DatabinderResponse{}, fmt.Errorf("bindType var must me set")
		}

		err = createDatabiner(databinder)
	}

	return &message_types.DatabinderResponse{}, err
}

func (s *server) Apply(ctx context.Context, r *message_types.DatabinderRequest) (*message_types.DatabinderResponse, error) {
	// create a slice for the errors
	var errstrings []string

	for _, element := range databinderArray {
		err := (*element).WriteAnalyzeResults(r.AnalyzeResults, r.Path)
		if err != nil {
			errstrings = append(errstrings, err.Error())
		}
		if r.AnonymizeResult != nil {
			log.Info(fmt.Sprintf("sending anonymized result: %s", r.Path))
			err := (*element).WriteAnonymizeResults(r.AnonymizeResult, r.Path)
			if err != nil {
				errstrings = append(errstrings, err.Error())
			}
		} else {
			log.Info(fmt.Sprintf("path %s has no anonymize result", r.Path))
		}

	}

	var combinedError error
	if len(errstrings) > 0 {
		combinedError = fmt.Errorf(strings.Join(errstrings, "\n"))
	}
	return &message_types.DatabinderResponse{}, combinedError
}
