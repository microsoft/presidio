package main

import (
	"encoding/json"
	"fmt"
	"os"

	context "golang.org/x/net/context"
	"google.golang.org/grpc/reflection"
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
	namespace               = os.Getenv("PRESIDIO_NAMESPACE")
	analyzerSvcAddress      = os.Getenv("ANALYZER_SVC_ADDRESS")
	anonymizerSvcAddress    = os.Getenv("ANONYMIZER_SVC_ADDRESS")
	redisURL                = os.Getenv("REDIS_URL")
	datasinkImage           = os.Getenv("DATASINK_IMAGE_NAME")
	scannerImage            = os.Getenv("SCANNER_IMAGE_NAME")
	streamsImage            = os.Getenv("STREAMS_IMAGE_NAME")
	datasinkImagePullPolicy = os.Getenv("DATASINK_IMAGE_PULL_POLICY")
	scannerImagePullPolicy  = os.Getenv("SCANNER_IMAGE_PULL_POLICY")
	streamsImagePullPolicy  = os.Getenv("STREAMS_IMAGE_PULL_POLICY")
	store                   platform.Store
)

const (
	envKubeConfig = "KUBECONFIG"
)

func main() {
	if grpcPort == "" {
		log.Fatal("GRPC_PORT (currently [%s]) env var must me set.", grpcPort)
	}
	if analyzerSvcAddress == "" {
		log.Fatal("analyzer service address is empty")
	}

	if anonymizerSvcAddress == "" {
		log.Fatal("anonymizer service address is empty")
	}

	if redisURL == "" {
		log.Fatal("redis service address is empty")
	}

	var err error
	log.Info("namespace %s", namespace)
	store, err = kube.New(namespace, "", kubeConfigPath())
	if err != nil {
		log.Fatal(err.Error())
	}

	lis, s := rpc.SetupClient(grpcPort)

	message_types.RegisterSchedulerServiceServer(s, &server{})
	reflection.Register(s)

	if err := s.Serve(lis); err != nil {
		log.Fatal(err.Error())
	}
}

func (s *server) ApplyScan(ctx context.Context, r *message_types.ScannerCronJobRequest) (*message_types.ScannerCronJobResponse, error) {
	_, err := applyScanRequest(r)
	return &message_types.ScannerCronJobResponse{}, err
}

func (s *server) ApplyStream(ctx context.Context, r *message_types.StreamsJobRequest) (*message_types.StreamsJobResponse, error) {
	_, err := applyStreamRequest(r)
	return &message_types.StreamsJobResponse{}, err
}

func applyScanRequest(r *message_types.ScannerCronJobRequest) (*message_types.ScannerCronJobResponse, error) {
	scanRequest, err := json.Marshal(r.ScanRequest)
	if err != nil {
		return &message_types.ScannerCronJobResponse{}, err
	}

	datasinkPolicy := platform.ConvertPullPolicyStringToType(datasinkImagePullPolicy)
	scannerPolicy := platform.ConvertPullPolicyStringToType(scannerImagePullPolicy)
	jobName := fmt.Sprintf("%s-scanner-cronjob", r.GetName())
	err = store.CreateCronJob(jobName, r.Trigger.Schedule.GetRecurrencePeriod(), []platform.ContainerDetails{
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
				{Name: "REDIS_URL", Value: redisURL},
				{Name: "ANALYZER_SVC_ADDRESS", Value: analyzerSvcAddress},
				{Name: "ANONYMIZER_SVC_ADDRESS", Value: anonymizerSvcAddress},
				{Name: "SCANNER_REQUEST", Value: string(scanRequest)},
			},
			ImagePullPolicy: scannerPolicy,
		},
	})
	return &message_types.ScannerCronJobResponse{}, err
}

func applyStreamRequest(r *message_types.StreamsJobRequest) (*message_types.StreamsJobResponse, error) {
	streamRequest, err := json.Marshal(r.StreamsRequest)
	if err != nil {
		return &message_types.StreamsJobResponse{}, err
	}

	datasinkPolicy := platform.ConvertPullPolicyStringToType(datasinkImagePullPolicy)
	streamsPolicy := platform.ConvertPullPolicyStringToType(streamsImagePullPolicy)

	for index := 0; index < 1; index++ {
		jobName := fmt.Sprintf("%s-streams-job-%d", r.GetName(), index)
		err = store.CreateJob(jobName, []platform.ContainerDetails{
			{
				Name:  "datasink",
				Image: datasinkImage,
				EnvVars: []apiv1.EnvVar{
					{Name: "DATASINK_GRPC_PORT", Value: datasinkGrpcPort},
				},
				ImagePullPolicy: datasinkPolicy,
			},
			{
				Name:  "streams",
				Image: streamsImage,
				EnvVars: []apiv1.EnvVar{
					{Name: "DATASINK_GRPC_PORT", Value: datasinkGrpcPort},
					{Name: "REDIS_URL", Value: redisURL},
					{Name: "ANALYZER_SVC_ADDRESS", Value: analyzerSvcAddress},
					{Name: "ANONYMIZER_SVC_ADDRESS", Value: anonymizerSvcAddress},
					{Name: "STREAM_REQUEST", Value: string(streamRequest)},
					{Name: "PARTITON_ID", Value: string(index)},
				},
				ImagePullPolicy: streamsPolicy,
			},
		})
	}

	return &message_types.StreamsJobResponse{}, err
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
