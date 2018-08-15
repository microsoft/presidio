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
	"github.com/Microsoft/presidio/presidio-datasink/cmd/presidio-datasink/datasink"
)

var (
	grpcPort           = os.Getenv("DATASINK_GRPC_PORT")
	analyzerDatasink   datasink.Datasink
	anonymizerDatasink datasink.Datasink
	grpcServer         *grpc.Server
	lis                net.Listener
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

	message_types.RegisterDatasinkServiceServer(grpcServer, &server{})
	reflection.Register(grpcServer)

	if err := grpcServer.Serve(lis); err != nil {
		log.Fatal(err.Error())
	}
}

func (s *server) Init(ctx context.Context, datasinkTemplate *message_types.DatasinkTemplate) (*message_types.DatasinkResponse, error) {
	if datasinkTemplate == nil || datasinkTemplate.Datasink == nil {
		return &message_types.DatasinkResponse{}, fmt.Errorf("datasinkTemplate must me set")
	}

	var err error

	// initialize each of the datasinks
	if datasinkTemplate.AnalyzerKind != "" {
		analyzerDatasink, err = createDatasink(datasinkTemplate.Datasink, datasinkTemplate.AnalyzerKind, "analyze")
		if err != nil {
			return &message_types.DatasinkResponse{}, err
		}
	}

	if datasinkTemplate.AnonymizerKind != "" {
		anonymizerDatasink, err = createDatasink(datasinkTemplate.Datasink, datasinkTemplate.AnonymizerKind, "anonymize")
		if err != nil {
			return &message_types.DatasinkResponse{}, err
		}
	}

	return &message_types.DatasinkResponse{}, err
}

func (s *server) Completion(ctx context.Context, completionMessage *message_types.CompletionMessage) (*message_types.DatasinkResponse, error) {
	log.Info("connection closed!")
	os.Exit(0)

	return &message_types.DatasinkResponse{}, nil
}

func (s *server) Apply(ctx context.Context, r *message_types.DatasinkRequest) (*message_types.DatasinkResponse, error) {
	// create a slice for the errors
	var errstrings []string

	if analyzerDatasink != nil {
		err := analyzerDatasink.WriteAnalyzeResults(r.AnalyzeResults, r.Path)
		if err != nil {
			errstrings = append(errstrings, err.Error())
		}
	}

	if anonymizerDatasink != nil {
		if r.AnonymizeResult != nil {
			log.Info("sending anonymized result: %s", r.Path)
			err := anonymizerDatasink.WriteAnonymizeResults(r.AnonymizeResult, r.Path)
			if err != nil {
				errstrings = append(errstrings, err.Error())
			}
		} else {
			log.Info("path %s has no anonymize result", r.Path)
		}
	}

	var combinedError error
	if len(errstrings) > 0 {
		combinedError = fmt.Errorf(strings.Join(errstrings, "\n"))
	}
	return &message_types.DatasinkResponse{}, combinedError
}
