package main

import (
	context "golang.org/x/net/context"
	"google.golang.org/grpc/reflection"

	"fmt"
	"os"

	message_types "github.com/presid-io/presidio-genproto/golang"
	log "github.com/presid-io/presidio/pkg/logger"
	"github.com/presid-io/presidio/pkg/rpc"
	handler "github.com/presid-io/presidio/presidio-anonymizer/cmd/presidio-anonymizer/anonymizer"
)

type server struct{}

var (
	grpcPort = os.Getenv("GRPC_PORT")
)

func main() {

	if grpcPort == "" {
		log.Fatal(fmt.Sprintf("GRPC_PORT (currently [%s]) env var must me set.", grpcPort))
	}

	lis, s := rpc.SetupClient(grpcPort)

	message_types.RegisterAnonymizeServiceServer(s, &server{})
	reflection.Register(s)

	if err := s.Serve(lis); err != nil {
		log.Fatal(err.Error())
	}

}

func (s *server) Apply(ctx context.Context, r *message_types.AnonymizeRequest) (*message_types.AnonymizeResponse, error) {
	res, err := handler.ApplyAnonymizerTemplate(r.Text, r.AnalyzeResults, r.Template)
	return &message_types.AnonymizeResponse{Text: res}, err
}
