package main

import (
	context "golang.org/x/net/context"
	"google.golang.org/grpc/reflection"

	"fmt"
	"os"

	message_types "github.com/presid-io/presidio-genproto/golang"
	log "github.com/presid-io/presidio/pkg/logger"
	"github.com/presid-io/presidio/pkg/rpc"
)

type server struct{}

var (
	grpcPort  = os.Getenv("GRPC_PORT")
	namespace = os.Getenv("presidio_NAMESPACE")
)

const (
	envKubeConfig = "KUBECONFIG"
)

func main() {

	if grpcPort == "" {
		log.Fatal(fmt.Sprintf("GRPC_PORT (currently [%s]) env var must me set.", grpcPort))
	}

	lis, s := rpc.SetupClient(grpcPort)

	message_types.RegisterJobServiceServer(s, &server{})
	reflection.Register(s)

	if err := s.Serve(lis); err != nil {
		log.Fatal(err.Error())
	}

}

func (s *server) Apply(ctx context.Context, r *message_types.JobRequest) (*message_types.JobResponse, error) {
	_, err := applySchedulerRequest(r)
	return &message_types.JobResponse{}, err
}

func applySchedulerRequest(r *message_types.JobRequest) (*message_types.JobResponse, error) {

	return &message_types.JobResponse{}, nil
}

// TODO: duplicate from api- refactor to pkg
func kubeConfigPath() string {
	if v, ok := os.LookupEnv(envKubeConfig); ok {
		return v
	}
	defConfig := os.ExpandEnv("$HOME/.kube/config")
	if _, err := os.Stat(defConfig); err == nil {
		log.Info("Using config from " + defConfig)
		return defConfig
	}

	// If we get here, we might be in-Pod.
	return ""
}
