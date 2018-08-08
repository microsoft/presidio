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
	"github.com/Microsoft/presidio/presidio-datasync/cmd/presidio-datasync/datasync"
)

var (
	grpcPort           = os.Getenv("GRPC_PORT")
	analyzerDataSync   dataSync.DataSync
	anonymizerDataSync dataSync.DataSync
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

	message_types.RegisterDataSyncServiceServer(grpcServer, &server{})
	reflection.Register(grpcServer)

	if err := grpcServer.Serve(lis); err != nil {
		log.Fatal(err.Error())
	}
}

func (s *server) Init(ctx context.Context, dataSyncTemplate *message_types.DataSyncTemplate) (*message_types.DataSyncResponse, error) {
	if dataSyncTemplate == nil || dataSyncTemplate.DataSync == nil {
		return &message_types.DataSyncResponse{}, fmt.Errorf("dataSyncTemplate must me set")
	}

	var err error

	// initialize each of the dataSyncs
	if dataSyncTemplate.AnalyzerKind != "" {
		analyzerDataSync, err = createDataSync(dataSyncTemplate.DataSync, dataSyncTemplate.AnalyzerKind, "analyze")
		if err != nil {
			return &message_types.DataSyncResponse{}, err
		}
	}

	if dataSyncTemplate.AnonymizerKind != "" {
		anonymizerDataSync, err = createDataSync(dataSyncTemplate.DataSync, dataSyncTemplate.AnonymizerKind, "anonymize")
		if err != nil {
			return &message_types.DataSyncResponse{}, err
		}
	}

	return &message_types.DataSyncResponse{}, err
}

func (s *server) Completion(ctx context.Context, completionMessage *message_types.CompletionMessage) (*message_types.DataSyncResponse, error) {
	log.Info("connection closed!")
	os.Exit(0)

	return &message_types.DataSyncResponse{}, nil
}

func (s *server) Apply(ctx context.Context, r *message_types.DataSyncRequest) (*message_types.DataSyncResponse, error) {
	// create a slice for the errors
	var errstrings []string

	if analyzerDataSync != nil {
		err := analyzerDataSync.WriteAnalyzeResults(r.AnalyzeResults, r.Path)
		if err != nil {
			errstrings = append(errstrings, err.Error())
		}
	}

	if anonymizerDataSync != nil {
		if r.AnonymizeResult != nil {
			log.Info(fmt.Sprintf("sending anonymized result: %s", r.Path))
			err := anonymizerDataSync.WriteAnonymizeResults(r.AnonymizeResult, r.Path)
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
	return &message_types.DataSyncResponse{}, combinedError
}
