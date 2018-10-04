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

//GetTrimmedEnv returns the spaces trimmed environment variable
func GetTrimmedEnv(key string) string {
	return strings.Trim(os.Getenv(key), " ")
}

//GetSettings from env vars
func GetSettings() *Settings {

	settings := Settings{
		WebPort:                  GetTrimmedEnv("WEB_PORT"),
		GrpcPort:                 GetTrimmedEnv("GRPC_PORT"),
		DatasinkGrpcPort:         GetTrimmedEnv("DATASINK_GRPC_PORT"),
		Namespace:                GetTrimmedEnv("PRESIDIO_NAMESPACE"),
		AnalyzerSvcAddress:       GetTrimmedEnv("ANALYZER_SVC_ADDRESS"),
		AnonymizerSvcAddress:     GetTrimmedEnv("ANONYMIZER_SVC_ADDRESS"),
		SchedulerSvcAddress:      GetTrimmedEnv("SCHEDULER_SVC_ADDRESS"),
		RedisURL:                 GetTrimmedEnv("REDIS_URL"),
		DatasinkImage:            GetTrimmedEnv("DATASINK_IMAGE_NAME"),
		CollectorImage:           GetTrimmedEnv("COLLECTOR_IMAGE_NAME"),
		DatasinkImagePullPolicy:  GetTrimmedEnv("DATASINK_IMAGE_PULL_POLICY"),
		CollectorImagePullPolicy: GetTrimmedEnv("COLLECTOR_IMAGE_PULL_POLICY"),
		ScannerRequest:           GetTrimmedEnv("SCANNER_REQUEST"),
		StreamRequest:            GetTrimmedEnv("STREAM_REQUEST"),
		QueueURL:                 GetTrimmedEnv("QUEUE_URL"),
	}

	return &settings
}
