package platform

import (
	"github.com/spf13/viper"
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

//GetSettings from env vars
func GetSettings() *Settings {

	viper.AutomaticEnv()

	settings := Settings{
		WebPort:                  viper.GetString("WEB_PORT"),
		GrpcPort:                 viper.GetString("GRPC_PORT"),
		DatasinkGrpcPort:         viper.GetString("DATASINK_GRPC_PORT"),
		Namespace:                viper.GetString("PRESIDIO_NAMESPACE"),
		AnalyzerSvcAddress:       viper.GetString("ANALYZER_SVC_ADDRESS"),
		AnonymizerSvcAddress:     viper.GetString("ANONYMIZER_SVC_ADDRESS"),
		SchedulerSvcAddress:      viper.GetString("SCHEDULER_SVC_ADDRESS"),
		RedisURL:                 viper.GetString("REDIS_URL"),
		DatasinkImage:            viper.GetString("DATASINK_IMAGE_NAME"),
		CollectorImage:           viper.GetString("COLLECTOR_IMAGE_NAME"),
		DatasinkImagePullPolicy:  viper.GetString("DATASINK_IMAGE_PULL_POLICY"),
		CollectorImagePullPolicy: viper.GetString("COLLECTOR_IMAGE_PULL_POLICY"),
		ScannerRequest:           viper.GetString("SCANNER_REQUEST"),
		StreamRequest:            viper.GetString("STREAM_REQUEST"),
		QueueURL:                 viper.GetString("QUEUE_URL"),
	}

	return &settings
}
