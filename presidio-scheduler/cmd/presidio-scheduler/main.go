package main

import (
	"encoding/json"

	context "golang.org/x/net/context"
	"google.golang.org/grpc/reflection"

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
	grpcPort                = os.Getenv("GRPC_PORT")
	datasinkGrpcPort        = os.Getenv("DATASINK_GRPC_PORT")
	namespace               = os.Getenv("presidio_NAMESPACE")
	analyzerSvcAddress      = os.Getenv("ANALYZER_SVC_ADDRESS")
	anonymizerSvcAddress    = os.Getenv("ANONYMIZER_SVC_ADDRESS")
	redisUrl                = os.Getenv("REDIS_URL")
	datasinkImage           = os.Getenv("DATASINK_IMAGE_NAME")
	scannerImage            = os.Getenv("SCANNER_IMAGE_NAME")
	datasinkImagePullPolicy = os.Getenv("DATASINK_IMAGE_PULL_POLICY")
	scannerImagePullPolicy  = os.Getenv("SCANNER_IMAGE_PULL_POLICY")
	store                   platform.Store
)

const (
	envKubeConfig = "KUBECONFIG"
)

func main() {
	log.Info("new version!")
	if grpcPort == "" {
		log.Fatal("GRPC_PORT (currently [%s]) env var must me set.", grpcPort)
	}
	if analyzerSvcAddress == "" {
		log.Fatal("analyzer service address is empty")
	}

	if anonymizerSvcAddress == "" {
		log.Fatal("anonymizer service address is empty")
	}

	if redisUrl == "" {
		log.Fatal("redis service address is empty")
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

	datasinkPolicy := platform.ConvertPullPolicyStringToType(datasinkImagePullPolicy)
	scannerPolicy := platform.ConvertPullPolicyStringToType(scannerImagePullPolicy)

	err = store.CreateCronJob(r.Name, r.Trigger.Schedule.GetRecurrencePeriodDuration(), []platform.ContainerDetails{
		{
			Name:  "datasink",
			Image: datasinkImage,
			EnvVars: []apiv1.EnvVar{
				{Name: "DATASINK_GRPC_PORT", Value: datasinkGrpcPort},
			},
			ImagePullPolicy: datasinkPolicy,
		},
		{
			Name:  "scanner",
			Image: scannerImage,
			EnvVars: []apiv1.EnvVar{
				{Name: "DATASINK_GRPC_PORT", Value: datasinkGrpcPort},
				{Name: "REDIS_URL", Value: redisUrl},
				{Name: "ANALYZER_SVC_ADRESS", Value: analyzerSvcAddress},
				{Name: "ANONYMIZER_SVC_ADDRESS", Value: anonymizerSvcAddress},
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
