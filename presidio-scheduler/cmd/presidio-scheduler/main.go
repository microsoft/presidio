package main

import (
	"encoding/json"
	"fmt"

	context "golang.org/x/net/context"
	"google.golang.org/grpc/reflection"
	apiv1 "k8s.io/api/core/v1"

	types "github.com/Microsoft/presidio-genproto/golang"
	log "github.com/Microsoft/presidio/pkg/logger"
	"github.com/Microsoft/presidio/pkg/platform"
	"github.com/Microsoft/presidio/pkg/platform/kube"
	"github.com/Microsoft/presidio/pkg/rpc"
)

type server struct{}

var (
	store    platform.Store
	settings *platform.Settings
)

func main() {
	settings = platform.GetSettings()
	if settings.GrpcPort == "" {
		log.Fatal("GRPC_PORT (currently [%s]) env var must me set.", settings.GrpcPort)
	}
	if settings.AnalyzerSvcAddress == "" {
		log.Fatal("analyzer service address is empty")
	}

	if settings.AnonymizerSvcAddress == "" {
		log.Fatal("anonymizer service address is empty")
	}

	if settings.RedisURL == "" {
		log.Fatal("redis service address is empty")
	}

	var err error
	log.Info("namespace %s", settings.Namespace)
	store, err = kube.New(settings.Namespace, "")
	if err != nil {
		log.Fatal(err.Error())
	}

	lis, s := rpc.SetupClient(settings.GrpcPort)

	types.RegisterSchedulerServiceServer(s, &server{})
	reflection.Register(s)

	if err := s.Serve(lis); err != nil {
		log.Fatal(err.Error())
	}
}

func (s *server) ApplyScan(ctx context.Context, r *types.ScannerCronJobRequest) (*types.ScannerCronJobResponse, error) {
	_, err := applyScanRequest(r)
	return &types.ScannerCronJobResponse{}, err
}

func (s *server) ApplyStream(ctx context.Context, r *types.StreamsJobRequest) (*types.StreamsJobResponse, error) {
	_, err := applyStreamRequest(r)
	return &types.StreamsJobResponse{}, err
}

func applyScanRequest(r *types.ScannerCronJobRequest) (*types.ScannerCronJobResponse, error) {
	scanRequest, err := json.Marshal(r.ScanRequest)
	if err != nil {
		return &types.ScannerCronJobResponse{}, err
	}

	datasinkPolicy := platform.ConvertPullPolicyStringToType(settings.DatasinkImagePullPolicy)
	scannerPolicy := platform.ConvertPullPolicyStringToType(settings.ScannerImagePullPolicy)
	jobName := fmt.Sprintf("%s-scanner-cronjob", r.GetName())
	err = store.CreateCronJob(jobName, r.Trigger.Schedule.GetRecurrencePeriod(), []platform.ContainerDetails{
		{
			Name:  "datasink",
			Image: settings.DatasinkImage,
			EnvVars: []apiv1.EnvVar{
				{Name: "DATASINK_GRPC_PORT", Value: settings.DatasinkGrpcPort},
			},
			ImagePullPolicy: datasinkPolicy,
		},
		{
			Name:  "scanner",
			Image: settings.ScannerImage,
			EnvVars: []apiv1.EnvVar{
				{Name: "DATASINK_GRPC_PORT", Value: settings.DatasinkGrpcPort},
				{Name: "REDIS_URL", Value: settings.RedisURL},
				{Name: "ANALYZER_SVC_ADDRESS", Value: settings.AnalyzerSvcAddress},
				{Name: "ANONYMIZER_SVC_ADDRESS", Value: settings.AnonymizerSvcAddress},
				{Name: "SCANNER_REQUEST", Value: string(scanRequest)},
			},
			ImagePullPolicy: scannerPolicy,
		},
	})
	return &types.ScannerCronJobResponse{}, err
}

func applyStreamRequest(r *types.StreamsJobRequest) (*types.StreamsJobResponse, error) {
	streamRequest, err := json.Marshal(r.StreamsRequest)
	if err != nil {
		return &types.StreamsJobResponse{}, err
	}

	datasinkPolicy := platform.ConvertPullPolicyStringToType(settings.DatasinkImagePullPolicy)
	streamsPolicy := platform.ConvertPullPolicyStringToType(settings.StreamsImagePullPolicy)

	for index := 0; index < 1; index++ {
		jobName := fmt.Sprintf("%s-streams-job-%d", r.GetName(), index)
		err = store.CreateJob(jobName, []platform.ContainerDetails{
			{
				Name:  "datasink",
				Image: settings.DatasinkImage,
				EnvVars: []apiv1.EnvVar{
					{Name: "DATASINK_GRPC_PORT", Value: settings.DatasinkGrpcPort},
				},
				ImagePullPolicy: datasinkPolicy,
			},
			{
				Name:  "streams",
				Image: settings.StreamsImage,
				EnvVars: []apiv1.EnvVar{
					{Name: "DATASINK_GRPC_PORT", Value: settings.DatasinkGrpcPort},
					{Name: "REDIS_URL", Value: settings.RedisURL},
					{Name: "ANALYZER_SVC_ADDRESS", Value: settings.AnalyzerSvcAddress},
					{Name: "ANONYMIZER_SVC_ADDRESS", Value: settings.AnonymizerSvcAddress},
					{Name: "STREAM_REQUEST", Value: string(streamRequest)},
					{Name: "PARTITON_ID", Value: string(index)},
				},
				ImagePullPolicy: streamsPolicy,
			},
		})
	}

	return &types.StreamsJobResponse{}, err
}
