package main

import (
	"encoding/json"
	"fmt"

	context "golang.org/x/net/context"
	"google.golang.org/grpc/reflection"
	apiv1 "k8s.io/api/core/v1"

	"github.com/spf13/pflag"
	"github.com/spf13/viper"

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

	pflag.Int("grpc_port", 3002, "GRPC listen port")
	pflag.Int("datasink_grpc_port", 5000, "Datasink GRPC listen port")
	pflag.String("analyzer_svc_address", "localhost:3000", "Analyzer service address")
	pflag.String("anonymizer_svc_address", "localhost:3001", "Anonymizer service address")
	pflag.String("redis_url", "localhost:6379", "Redis address")

	pflag.Parse()
	viper.BindPFlags(pflag.CommandLine)

	settings = platform.GetSettings()

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

	if settings == nil {
		return &types.ScannerCronJobResponse{}, fmt.Errorf("Settings is null")
	}
	if r.Trigger.Schedule == nil {
		return &types.ScannerCronJobResponse{}, fmt.Errorf("Trigger schedule is null")
	}

	datasinkPolicy := platform.ConvertPullPolicyStringToType(settings.DatasinkImagePullPolicy)
	collectorPolicy := platform.ConvertPullPolicyStringToType(settings.CollectorImagePullPolicy)
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
			Image: settings.CollectorImage,
			EnvVars: []apiv1.EnvVar{
				{Name: "DATASINK_GRPC_PORT", Value: settings.DatasinkGrpcPort},
				{Name: "REDIS_URL", Value: settings.RedisURL},
				{Name: "ANALYZER_SVC_ADDRESS", Value: settings.AnalyzerSvcAddress},
				{Name: "ANONYMIZER_SVC_ADDRESS", Value: settings.AnonymizerSvcAddress},
				{Name: "SCANNER_REQUEST", Value: string(scanRequest)},
			},
			ImagePullPolicy: collectorPolicy,
		},
	})
	return &types.ScannerCronJobResponse{}, err
}

func applyStreamRequest(r *types.StreamsJobRequest) (*types.StreamsJobResponse, error) {
	streamRequest, err := json.Marshal(r.StreamsRequest)
	if err != nil {
		return &types.StreamsJobResponse{}, err
	}

	if settings == nil {
		return &types.StreamsJobResponse{}, fmt.Errorf("Settings is null")
	}

	if r.StreamsRequest.StreamConfig == nil {
		return &types.StreamsJobResponse{}, fmt.Errorf("Stream config is null")
	}

	datasinkPolicy := platform.ConvertPullPolicyStringToType(settings.DatasinkImagePullPolicy)
	collectorPolicy := platform.ConvertPullPolicyStringToType(settings.CollectorImagePullPolicy)

	partitionCount := int(r.StreamsRequest.GetStreamConfig().PartitionCount)
	for index := 0; index < partitionCount; index++ {
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
				Image: settings.CollectorImage,
				EnvVars: []apiv1.EnvVar{
					{Name: "DATASINK_GRPC_PORT", Value: settings.DatasinkGrpcPort},
					{Name: "REDIS_URL", Value: settings.RedisURL},
					{Name: "ANALYZER_SVC_ADDRESS", Value: settings.AnalyzerSvcAddress},
					{Name: "ANONYMIZER_SVC_ADDRESS", Value: settings.AnonymizerSvcAddress},
					{Name: "STREAM_REQUEST", Value: string(streamRequest)},
				},
				ImagePullPolicy: collectorPolicy,
			},
		})
	}

	return &types.StreamsJobResponse{}, err
}
