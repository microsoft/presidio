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
	grpcPort                = os.Getenv("DATASINK_GRPC_PORT")
	analyzerDatasinkArray   []datasink.Datasink
	anonymizerDatasinkArray []datasink.Datasink
	grpcServer              *grpc.Server
	lis                     net.Listener
)

type server struct{}

func main() {

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
	if datasinkTemplate == nil || (datasinkTemplate.AnalyzeDatasink == nil && datasinkTemplate.AnonymizeDatasink == nil) {
		return &message_types.DatasinkResponse{}, fmt.Errorf("AnalyzeDatasink or AnonymizeDatasink must me set")
	}

	// initialize each of the datasinks
	if datasinkTemplate.GetAnalyzeDatasink() != nil {
		for _, datasink := range datasinkTemplate.GetAnalyzeDatasink() {
			analyzerDatasink, err := createDatasink(datasink, "analyze")
			if err != nil {
				return &message_types.DatasinkResponse{}, err
			}
			analyzerDatasinkArray = append(analyzerDatasinkArray, analyzerDatasink)
		}
	}

	if datasinkTemplate.GetAnonymizeDatasink() != nil {
		for _, datasink := range datasinkTemplate.GetAnonymizeDatasink() {
			anonymizerDatasink, err := createDatasink(datasink, "anonymize")
			if err != nil {
				return &message_types.DatasinkResponse{}, err
			}
			anonymizerDatasinkArray = append(anonymizerDatasinkArray, anonymizerDatasink)
		}
	}

	return &message_types.DatasinkResponse{}, nil
}

func (s *server) Completion(ctx context.Context, completionMessage *message_types.CompletionMessage) (*message_types.DatasinkResponse, error) {
	log.Info("connection closed!")
	os.Exit(0)

	return &message_types.DatasinkResponse{}, nil
}

func (s *server) Apply(ctx context.Context, r *message_types.DatasinkRequest) (*message_types.DatasinkResponse, error) {
	// create a slice for the errors
	var errstrings []string

	for _, datasink := range analyzerDatasinkArray {
		err := datasink.WriteAnalyzeResults(r.AnalyzeResults, r.Path)
		if err != nil {
			errstrings = append(errstrings, err.Error())
		}
	}

	for _, datasink := range anonymizerDatasinkArray {
		if r.AnonymizeResult != nil {
			log.Info("sending anonymized result: %s", r.Path)
			err := datasink.WriteAnonymizeResults(r.AnonymizeResult, r.Path)
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
