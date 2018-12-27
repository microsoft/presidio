package main

import (
	"context"
	"flag"
	"fmt"
	"net"
	"os"
	"strings"

	"github.com/spf13/pflag"
	"github.com/spf13/viper"

	log "github.com/Microsoft/presidio/pkg/logger"

	"google.golang.org/grpc"
	"google.golang.org/grpc/reflection"

	types "github.com/Microsoft/presidio-genproto/golang"

	"github.com/Microsoft/presidio/pkg/platform"
	"github.com/Microsoft/presidio/pkg/rpc"
	"github.com/Microsoft/presidio/presidio-datasink/cmd/presidio-datasink/datasink"
)

var (
	analyzerDatasinkArray   []datasink.Datasink
	anonymizerDatasinkArray []datasink.Datasink
	grpcServer              *grpc.Server
	lis                     net.Listener
)

type server struct{}

func main() {

	pflag.Int(platform.DatasinkGrpcPort, 5000, "GRPC listen port")
	pflag.String("log_level", "info", "Log level - debug/info/warn/error")

	pflag.CommandLine.AddGoFlagSet(flag.CommandLine)
	pflag.Parse()
	viper.BindPFlags(pflag.CommandLine)

	settings := platform.GetSettings()
	log.CreateLogger(settings.LogLevel)

	// Setup server
	lis, grpcServer = rpc.SetupClient(settings.DatasinkGrpcPort)

	types.RegisterDatasinkServiceServer(grpcServer, &server{})
	reflection.Register(grpcServer)

	if err := grpcServer.Serve(lis); err != nil {
		log.Fatal(err.Error())
	}
}

func (s *server) Init(ctx context.Context, datasinkTemplate *types.DatasinkTemplate) (*types.DatasinkResponse, error) {
	if datasinkTemplate == nil || (datasinkTemplate.AnalyzeDatasink == nil && datasinkTemplate.AnonymizeDatasink == nil) {
		return &types.DatasinkResponse{}, fmt.Errorf("AnalyzeDatasink or AnonymizeDatasink must me set")
	}

	// initialize each of the datasinks
	if datasinkTemplate.GetAnalyzeDatasink() != nil {
		for _, datasink := range datasinkTemplate.GetAnalyzeDatasink() {
			analyzerDatasink, err := createDatasink(datasink, "analyze")
			if err != nil {
				return &types.DatasinkResponse{}, err
			}
			analyzerDatasinkArray = append(analyzerDatasinkArray, analyzerDatasink)
		}
	}

	if datasinkTemplate.GetAnonymizeDatasink() != nil {
		for _, datasink := range datasinkTemplate.GetAnonymizeDatasink() {
			anonymizerDatasink, err := createDatasink(datasink, "anonymize")
			if err != nil {
				return &types.DatasinkResponse{}, err
			}
			anonymizerDatasinkArray = append(anonymizerDatasinkArray, anonymizerDatasink)
		}
	}

	return &types.DatasinkResponse{}, nil
}

func (s *server) Completion(ctx context.Context, completionMessage *types.CompletionMessage) (*types.DatasinkResponse, error) {
	log.Info("connection closed!")
	os.Exit(0)

	return &types.DatasinkResponse{}, nil
}

func (s *server) Apply(ctx context.Context, r *types.DatasinkRequest) (*types.DatasinkResponse, error) {
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
	return &types.DatasinkResponse{}, combinedError
}
