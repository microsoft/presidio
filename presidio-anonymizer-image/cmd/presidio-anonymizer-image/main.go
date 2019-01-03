package main

import (
	"flag"

	context "golang.org/x/net/context"
	"google.golang.org/grpc/reflection"

	types "github.com/Microsoft/presidio-genproto/golang"

	"github.com/spf13/pflag"
	"github.com/spf13/viper"

	log "github.com/Microsoft/presidio/pkg/logger"
	"github.com/Microsoft/presidio/pkg/platform"
	"github.com/Microsoft/presidio/pkg/rpc"
	"github.com/Microsoft/presidio/presidio-anonymizer-image/cmd/presidio-anonymizer-image/anonymizer"
)

type server struct{}

func main() {

	pflag.Int(platform.GrpcPort, 3002, "GRPC listen port")
	pflag.String("log_level", "info", "Log level - debug/info/warn/error")

	pflag.CommandLine.AddGoFlagSet(flag.CommandLine)
	pflag.Parse()
	viper.BindPFlags(pflag.CommandLine)

	settings := platform.GetSettings()
	log.CreateLogger(settings.LogLevel)

	lis, s := rpc.SetupClient(settings.GrpcPort)

	types.RegisterAnonymizeImageServiceServer(s, &server{})
	reflection.Register(s)
	if err := s.Serve(lis); err != nil {
		log.Fatal(err.Error())
	}

}

func (s *server) Apply(ctx context.Context, r *types.AnonymizeImageRequest) (*types.AnonymizeImageResponse, error) {

	res, err := anonymizer.AnonymizeImage(r.Image, r.DetectionType, r.AnalyzeResults, r.Template)
	if err != nil {
		log.Error(err.Error())
	}
	return &types.AnonymizeImageResponse{Image: res}, err
}
