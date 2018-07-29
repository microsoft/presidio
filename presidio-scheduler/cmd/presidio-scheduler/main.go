package main

import (
	"encoding/json"

	context "golang.org/x/net/context"
	"google.golang.org/grpc/reflection"

	"fmt"
	"os"

	apiv1 "k8s.io/api/core/v1"

	message_types "github.com/presid-io/presidio-genproto/golang"
	log "github.com/presid-io/presidio/pkg/logger"
	"github.com/presid-io/presidio/pkg/platform"
	"github.com/presid-io/presidio/pkg/platform/kube"
	"github.com/presid-io/presidio/pkg/rpc"
)

type server struct{}

var (
	grpcPort        = os.Getenv("GRPC_PORT")
	namespace       = os.Getenv("presidio_NAMESPACE")
	analyzerSvcHost = os.Getenv("ANALYZER_SVC_HOST")
	analyzerSvcPort = os.Getenv("ANALYZER_SVC_PORT")
	// redisSvcHost    = os.Getenv("REDIS_SVC_HOST")
	// redisSvcPort    = os.Getenv("REDIS_SVC_PORT")
	store platform.Store
)

const (
	envKubeConfig = "KUBECONFIG"
)

func main() {
	if grpcPort == "" {
		log.Fatal(fmt.Sprintf("GRPC_PORT (currently [%s]) env var must me set.", grpcPort))
	}
	if analyzerSvcHost == "" {
		log.Fatal("analyzer service address is empty")
	}
	if analyzerSvcPort == "" {
		log.Fatal("analyzer service port is empty")
	}

	// if redisSvcHost == "" {
	// 	log.Fatal("redis service address is empty")
	// }

	// if redisSvcPort == "" {
	// 	log.Fatal("redis service port is empty")
	// }

	var err error
	store, err = kube.New(namespace, "", kubeConfigPath())
	if err != nil {
		log.Fatal(err.Error())
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
	scanRequest, err := json.Marshal(r.ScanRequest)
	if err != nil {
		return &message_types.JobResponse{}, err
	}

	//s := &store
	err = store.CreateCronJob(r.Name, r.Trigger.Schedule.GetRecurrencePeriodDuration(), []platform.ContainerDetails{
		platform.ContainerDetails{
			Name:  "databinder",
			Image: "praesidio/presidio-databinder:latest",
			EnvVars: []apiv1.EnvVar{
				apiv1.EnvVar{Name: "GRPC_PORT", Value: "5000"},
			},
		},
		platform.ContainerDetails{
			Name:  "scanner",
			Image: "praesidio/presidio-scanner:latest",
			EnvVars: []apiv1.EnvVar{
				apiv1.EnvVar{Name: "GRPC_PORT", Value: "5000"},
				apiv1.EnvVar{Name: "REDIS_HOST", Value: "redis-master.presidio-system.svc.cluster.local"},
				apiv1.EnvVar{Name: "REDIS_SVC_PORT", Value: "6379"},
				apiv1.EnvVar{Name: "ANALYZER_SVC_HOST", Value: analyzerSvcHost},
				apiv1.EnvVar{Name: "ANALYZER_SVC_PORT", Value: analyzerSvcPort},
				apiv1.EnvVar{Name: "SCANNER_REQUEST", Value: string(scanRequest)},
			},
		},
	})
	return &message_types.JobResponse{}, err
}

// TODO: duplication from presidio api- refactor to pkg
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
