package main

import (
	context "golang.org/x/net/context"
	"google.golang.org/grpc/reflection"

	types "github.com/Microsoft/presidio-genproto/golang"

	log "github.com/Microsoft/presidio/pkg/logger"
	"github.com/Microsoft/presidio/pkg/platform"
	"github.com/Microsoft/presidio/pkg/rpc"

	"github.com/Microsoft/presidio/presidio-anonymizer/cmd/presidio-anonymizer/anonymizer"
)

type server struct{}

func main() {

	settings := platform.GetSettings()

	if settings.GrpcPort == "" {
		log.Fatal("GRPC_PORT (currently [%s]) env var must me set.", settings.GrpcPort)
	}

	lis, s := rpc.SetupClient(settings.GrpcPort)

	types.RegisterAnonymizeServiceServer(s, &server{})
	reflection.Register(s)

	if err := s.Serve(lis); err != nil {
		log.Fatal(err.Error())
	}

}

func (s *server) Apply(ctx context.Context, r *types.AnonymizeRequest) (*types.AnonymizeResponse, error) {
	res, err := anonymizer.ApplyAnonymizerTemplate(r.Text, r.AnalyzeResults, r.Template)
	return &types.AnonymizeResponse{Text: res}, err
}
