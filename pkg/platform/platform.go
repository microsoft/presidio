package platform

import (
	"os"

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
	WebPort                 string
	GrpcPort                string
	DatasinkGrpcPort        string
	Namespace               string
	AnalyzerSvcAddress      string
	AnonymizerSvcAddress    string
	SchedulerSvcAddress     string
	RedisURL                string
	DatasinkImage           string
	ScannerImage            string
	StreamsImage            string
	DatasinkImagePullPolicy string
	ScannerImagePullPolicy  string
	StreamsImagePullPolicy  string
	ScannerRequest          string
	StreamRequest           string
}

//GetSettings from env vars
func GetSettings() *Settings {

	settings := Settings{
		WebPort:                 os.Getenv("WEB_PORT"),
		GrpcPort:                os.Getenv("GRPC_PORT"),
		DatasinkGrpcPort:        os.Getenv("DATASINK_GRPC_PORT"),
		Namespace:               os.Getenv("PRESIDIO_NAMESPACE"),
		AnalyzerSvcAddress:      os.Getenv("ANALYZER_SVC_ADDRESS"),
		AnonymizerSvcAddress:    os.Getenv("ANONYMIZER_SVC_ADDRESS"),
		SchedulerSvcAddress:     os.Getenv("SCHEDULER_SVC_ADDRESS"),
		RedisURL:                os.Getenv("REDIS_URL"),
		DatasinkImage:           os.Getenv("DATASINK_IMAGE_NAME"),
		ScannerImage:            os.Getenv("SCANNER_IMAGE_NAME"),
		StreamsImage:            os.Getenv("STREAMS_IMAGE_NAME"),
		DatasinkImagePullPolicy: os.Getenv("DATASINK_IMAGE_PULL_POLICY"),
		ScannerImagePullPolicy:  os.Getenv("SCANNER_IMAGE_PULL_POLICY"),
		StreamsImagePullPolicy:  os.Getenv("STREAMS_IMAGE_PULL_POLICY"),
		ScannerRequest:          os.Getenv("SCANNER_REQUEST"),
		StreamRequest:           os.Getenv("STREAM_REQUEST"),
	}

	return &settings
}
