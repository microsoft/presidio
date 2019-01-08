package main

import (
	"context"
	"flag"

	"google.golang.org/grpc/reflection"

	types "github.com/Microsoft/presidio-genproto/golang"

	"github.com/spf13/pflag"
	"github.com/spf13/viper"

	log "github.com/Microsoft/presidio/pkg/logger"
	"github.com/Microsoft/presidio/pkg/platform"
	"github.com/Microsoft/presidio/pkg/rpc"
	"github.com/Microsoft/presidio/presidio-ocr/cmd/presidio-ocr/ocr"
)

type server struct{}

func main() {

	pflag.Int(platform.GrpcPort, 3003, "GRPC listen port")
	pflag.String("log_level", "info", "Log level - debug/info/warn/error")

	pflag.CommandLine.AddGoFlagSet(flag.CommandLine)
	pflag.Parse()
	viper.BindPFlags(pflag.CommandLine)

	settings := platform.GetSettings()
	log.CreateLogger(settings.LogLevel)

	lis, s := rpc.SetupClient(settings.GrpcPort)

	types.RegisterOcrServiceServer(s, &server{})
	reflection.Register(s)
	if err := s.Serve(lis); err != nil {
		log.Fatal(err.Error())
	}

}

func (s *server) Apply(ctx context.Context, r *types.OcrRequest) (*types.OcrResponse, error) {

	res, err := ocr.PerformOCR(r.Image)
	if err != nil {
		log.Error(err.Error())
	}

	return &types.OcrResponse{Image: res}, err
}
