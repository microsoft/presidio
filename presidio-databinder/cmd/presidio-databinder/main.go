package main

import (
	"context"
	"fmt"
	"net"
	"os"
	"strings"

	log "github.com/Microsoft/presidio/pkg/logger"

	"google.golang.org/grpc"
	"google.golang.org/grpc/reflection"

	message_types "github.com/Microsoft/presidio-genproto/golang"
	"github.com/Microsoft/presidio/pkg/rpc"
	"github.com/Microsoft/presidio/presidio-databinder/cmd/presidio-databinder/databinder"
)

var (
	grpcPort             = os.Getenv("GRPC_PORT")
	analyzerDataBinder   databinder.DataBinder
	anonymizerDataBinder databinder.DataBinder
	grpcServer           *grpc.Server
	lis                  net.Listener
)

type server struct{}

func main() {
	log.Info("starting!")
	if grpcPort == "" {
		// Set to default
		grpcPort = "5000"
	}

	// Setup server
	lis, grpcServer = rpc.SetupClient(grpcPort)

	message_types.RegisterDatabinderServiceServer(grpcServer, &server{})
	reflection.Register(grpcServer)

	if err := grpcServer.Serve(lis); err != nil {
		log.Fatal(err.Error())
	}
}

func (s *server) Init(ctx context.Context, databinderTemplate *message_types.DatabinderTemplate) (*message_types.DatabinderResponse, error) {
	if databinderTemplate == nil || databinderTemplate.Databinder == nil {
		return &message_types.DatabinderResponse{}, fmt.Errorf("databinderTemplate must me set")
	}

	var err error

	// initialize each of the databinders
	if databinderTemplate.AnalyzerKind != "" {
		analyzerDataBinder, err = createDatabiner(databinderTemplate.Databinder, databinderTemplate.AnalyzerKind, "analyze")
		if err != nil {
			return &message_types.DatabinderResponse{}, err
		}
	}

	if databinderTemplate.AnonymizerKind != "" {
		anonymizerDataBinder, err = createDatabiner(databinderTemplate.Databinder, databinderTemplate.AnonymizerKind, "anonymize")
		if err != nil {
			return &message_types.DatabinderResponse{}, err
		}
	}

	return &message_types.DatabinderResponse{}, err
}

func (s *server) Completion(ctx context.Context, completionMessage *message_types.CompletionMessage) (*message_types.DatabinderResponse, error) {
	log.Info("connection closed!")
	os.Exit(0)

	return &message_types.DatabinderResponse{}, nil
}

func (s *server) Apply(ctx context.Context, r *message_types.DatabinderRequest) (*message_types.DatabinderResponse, error) {
	// create a slice for the errors
	var errstrings []string

	if analyzerDataBinder != nil {
		err := analyzerDataBinder.WriteAnalyzeResults(r.AnalyzeResults, r.Path)
		if err != nil {
			errstrings = append(errstrings, err.Error())
		}
	}

	if anonymizerDataBinder != nil {
		if r.AnonymizeResult != nil {
			log.Info(fmt.Sprintf("sending anonymized result: %s", r.Path))
			err := anonymizerDataBinder.WriteAnonymizeResults(r.AnonymizeResult, r.Path)
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
