package platform

import (
	"os"
	"strings"

	apiv1 "k8s.io/api/core/v1"

	log "github.com/Microsoft/presidio/pkg/logger"
)

//ContainerDetails ...
type ContainerDetails struct {
	Name            string
	Image           string
	EnvVars         []apiv1.EnvVar
	ImagePullPolicy apiv1.PullPolicy
}

//Store interface
type Store interface {
	PutKVPair(key string, value string) error
	GetKVPair(key string) (string, error)
	DeleteKVPair(key string) error
	CreateJob(name string, containerDetailsArray []ContainerDetails) error
	CreateCronJob(name string, schedule string, containerDetailsArray []ContainerDetails) error
	ListJobs() ([]string, error)
	ListCronJobs() ([]string, error)
	DeleteJob(name string) error
	DeleteCronJob(name string) error
}

// ConvertPullPolicyStringToType converts job policy string to pull polcy type
func ConvertPullPolicyStringToType(pullPolicy string) apiv1.PullPolicy {
	switch pullPolicy {
	case "Always":
		return apiv1.PullAlways
	case "Never":
		return apiv1.PullNever
	case "IfNotPresent":
		return apiv1.PullIfNotPresent
	default:
		log.Info("Unknown pull policy type %s, setting default to always", pullPolicy)
		return apiv1.PullAlways
	}
}

//Settings from all services
type Settings struct {
	WebPort                  string
	GrpcPort                 string
	DatasinkGrpcPort         string
	Namespace                string
	AnalyzerSvcAddress       string
	AnonymizerSvcAddress     string
	SchedulerSvcAddress      string
	RedisURL                 string
	DatasinkImage            string
	CollectorImage           string
	DatasinkImagePullPolicy  string
	CollectorImagePullPolicy string
	ScannerRequest           string
	StreamRequest            string
	QueueURL                 string
}

//getTrimmedEnv returns the spaces trimmed environment variable
func getTrimmedEnv(key string) string {
	return strings.Trim(os.Getenv(key), " ")
}

//GetSettings from env vars
func GetSettings() *Settings {

	settings := Settings{
		WebPort:                  getTrimmedEnv("WEB_PORT"),
		GrpcPort:                 getTrimmedEnv("GRPC_PORT"),
		DatasinkGrpcPort:         getTrimmedEnv("DATASINK_GRPC_PORT"),
		Namespace:                getTrimmedEnv("PRESIDIO_NAMESPACE"),
		AnalyzerSvcAddress:       getTrimmedEnv("ANALYZER_SVC_ADDRESS"),
		AnonymizerSvcAddress:     getTrimmedEnv("ANONYMIZER_SVC_ADDRESS"),
		SchedulerSvcAddress:      getTrimmedEnv("SCHEDULER_SVC_ADDRESS"),
		RedisURL:                 getTrimmedEnv("REDIS_URL"),
		DatasinkImage:            getTrimmedEnv("DATASINK_IMAGE_NAME"),
		CollectorImage:           getTrimmedEnv("COLLECTOR_IMAGE_NAME"),
		DatasinkImagePullPolicy:  getTrimmedEnv("DATASINK_IMAGE_PULL_POLICY"),
		CollectorImagePullPolicy: getTrimmedEnv("COLLECTOR_IMAGE_PULL_POLICY"),
		ScannerRequest:           getTrimmedEnv("SCANNER_REQUEST"),
		StreamRequest:            getTrimmedEnv("STREAM_REQUEST"),
		QueueURL:                 getTrimmedEnv("QUEUE_URL"),
	}

	return &settings
}
