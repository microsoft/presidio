package main

import (
	"encoding/json"

	context "golang.org/x/net/context"
	"google.golang.org/grpc/reflection"

	"fmt"
	"os"

	apiv1 "k8s.io/api/core/v1"

	message_types "github.com/Microsoft/presidio-genproto/golang"
	log "github.com/Microsoft/presidio/pkg/logger"
	"github.com/Microsoft/presidio/pkg/platform"
	"github.com/Microsoft/presidio/pkg/platform/kube"
	"github.com/Microsoft/presidio/pkg/rpc"
)

type server struct{}

var (
	grpcPort = os.Getenv("GRPC_PORT")
	// Currently not supported, will be in use once we'll move to configmaps. default port is 5000
	dataSyncGrpcPort        = os.Getenv("DATASYNC_GRPC_PORT")
	namespace               = os.Getenv("presidio_NAMESPACE")
	analyzerSvcHost         = os.Getenv("ANALYZER_SVC_HOST")
	analyzerSvcPort         = os.Getenv("ANALYZER_SVC_PORT")
	anonymizerSvcHost       = os.Getenv("ANONYMIZER_SVC_HOST")
	anonymizerSvcPort       = os.Getenv("ANONYMIZER_SVC_PORT")
	redisSvcHost            = os.Getenv("REDIS_HOST")
	redisSvcPort            = os.Getenv("REDIS_PORT")
	dataSyncImage           = os.Getenv("DATASYNC_IMAGE_NAME")
	scannerImage            = os.Getenv("SCANNER_IMAGE_NAME")
	dataSyncImagePullPolicy = os.Getenv("DATASYNC_IMAGE_PULL_POLICY")
	scannerImagePullPolicy  = os.Getenv("SCANNER_IMAGE_PULL_POLICY")
	store                   platform.Store
)

const (
	envKubeConfig = "KUBECONFIG"
)

func main() {
	log.Info("new version!")
	if grpcPort == "" {
		log.Fatal(fmt.Sprintf("GRPC_PORT (currently [%s]) env var must me set.", grpcPort))
	}
	if analyzerSvcHost == "" {
		log.Fatal("analyzer service address is empty")
	}
	if analyzerSvcPort == "" {
		log.Fatal("analyzer service port is empty")
	}

	if anonymizerSvcHost == "" {
		log.Fatal("anonymizer service address is empty")
	}
	if anonymizerSvcPort == "" {
		log.Fatal("anonymizer service port is empty")
	}

	if redisSvcHost == "" {
		log.Fatal("redis service address is empty")
	}

	if redisSvcPort == "" {
		log.Fatal("redis service port is empty")
	}

	var err error
	store, err = kube.New(namespace, "", kubeConfigPath())
	if err != nil {
		log.Fatal(err.Error())
	}

	lis, s := rpc.SetupClient(grpcPort)

	message_types.RegisterCronJobServiceServer(s, &server{})
	reflection.Register(s)

	if err := s.Serve(lis); err != nil {
		log.Fatal(err.Error())
	}
}

func (s *server) Apply(ctx context.Context, r *message_types.CronJobRequest) (*message_types.CronJobResponse, error) {
	_, err := applySchedulerRequest(r)
	return &message_types.CronJobResponse{}, err
}

func applySchedulerRequest(r *message_types.CronJobRequest) (*message_types.CronJobResponse, error) {
	scanRequest, err := json.Marshal(r.ScanRequest)
	if err != nil {
		return &message_types.CronJobResponse{}, err
	}

	dataSyncPolicy := platform.ConvertPullPolicyStringToType(dataSyncImagePullPolicy)
	scannerPolicy := platform.ConvertPullPolicyStringToType(scannerImagePullPolicy)

	err = store.CreateCronJob(r.Name, r.Trigger.Schedule.GetRecurrencePeriodDuration(), []platform.ContainerDetails{
		{
			Name:  "datasync",
			Image: dataSyncImage,
			EnvVars: []apiv1.EnvVar{
				{Name: "GRPC_PORT", Value: dataSyncGrpcPort},
			},
			ImagePullPolicy: dataSyncPolicy,
		},
		{
			Name:  "scanner",
			Image: scannerImage,
			EnvVars: []apiv1.EnvVar{
				{Name: "GRPC_PORT", Value: dataSyncGrpcPort},
				{Name: "REDIS_HOST", Value: redisSvcHost},
				{Name: "REDIS_SVC_PORT", Value: redisSvcPort},
				{Name: "ANALYZER_SVC_HOST", Value: analyzerSvcHost},
				{Name: "ANALYZER_SVC_PORT", Value: analyzerSvcPort},
				{Name: "ANONYMIZER_SVC_HOST", Value: anonymizerSvcHost},
				{Name: "ANONYMIZER_SVC_PORT", Value: anonymizerSvcPort},
				{Name: "SCANNER_REQUEST", Value: string(scanRequest)},
			},
			ImagePullPolicy: scannerPolicy,
		},
	})
	return &message_types.CronJobResponse{}, err
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
