package platform

import (
	"strings"

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
	WebPort                    int
	GrpcPort                   int
	DatasinkGrpcPort           int
	Namespace                  string
	AnalyzerSvcAddress         string
	AnonymizerSvcAddress       string
	AnonymizerImageSvcAddress  string
	OcrSvcAddress              string
	SchedulerSvcAddress        string
	RecognizersStoreSvcAddress string
	APISvcAddress              string
	RedisURL                   string
	RedisPassword              string
	RedisDB                    int
	RedisSSL                   bool
	DatasinkImage              string
	CollectorImage             string
	DatasinkImagePullPolicy    string
	CollectorImagePullPolicy   string
	ScannerRequest             string
	StreamRequest              string
	QueueURL                   string
	LogLevel                   string
	RecognizersStoreGrpcPort   int
}

//WebPort for http server
const WebPort = "web_port"

//GrpcPort for GRPC server
const GrpcPort = "grpc_port"

//DatasinkGrpcPort for data sink GRPC server
const DatasinkGrpcPort = "datasink_grpc_port"

//RecognizersStoreGrpcPort for data sink GRPC server
const RecognizersStoreGrpcPort = "recognizers_store_grpc_port"

//PresidioNamespace for k8s deployment
const PresidioNamespace = "presidio_namespace"

//AnalyzerSvcAddress analyzer service address
const AnalyzerSvcAddress = "analyzer_svc_address"

//AnonymizerSvcAddress anonymizer service address
const AnonymizerSvcAddress = "anonymizer_svc_address"

//AnonymizerImageSvcAddress anonymizer image service address
const AnonymizerImageSvcAddress = "anonymizer_image_svc_address"

//OcrSvcAddress ocr service address
const OcrSvcAddress = "ocr_svc_address"

//SchedulerSvcAddress scheduler service address
const SchedulerSvcAddress = "scheduler_svc_address"

//RecognizersStoreSvcAddress recognizers store service address
const RecognizersStoreSvcAddress = "recognizers_store_svc_address"

//APISvcAddress api service address
const APISvcAddress = "api_svc_address"

//RedisURL redis address
const RedisURL = "redis_url"

//RedisDb redis db number
const RedisDb = "redis_db"

//RedisSSL redis ssl
const RedisSSL = "redis_ssl"

//RedisPassword redis db password
const RedisPassword = "redis_password"

//DatasinkImageName datasink docker image name
const DatasinkImageName = "datasink_image_name"

//DatasinkImagePullPolicy datasink image k8s pull policy
const DatasinkImagePullPolicy = "datasink_image_pull_policy"

//CollectorImageName collector docker image name
const CollectorImageName = "collector_image_name"

//CollectorImagePullPolicy collector image k8s pull policy
const CollectorImagePullPolicy = "collector_image_pull_policy"

//ScannerRequest template
const ScannerRequest = "scanner_request"

//StreamRequest template
const StreamRequest = "stream_request"

//QueueURL rabbitmq url
const QueueURL = "queue_url"

//LogLevel debug/info/warn/error/fatal
const LogLevel = "log_level"

//GetSettings from env vars
func GetSettings() *Settings {

	viper.AutomaticEnv()

	settings := Settings{
		WebPort:                    viper.GetInt(strings.ToUpper(WebPort)),
		GrpcPort:                   viper.GetInt(strings.ToUpper(GrpcPort)),
		DatasinkGrpcPort:           viper.GetInt(strings.ToUpper(DatasinkGrpcPort)),
		RecognizersStoreGrpcPort:   viper.GetInt(strings.ToUpper(RecognizersStoreGrpcPort)),
		Namespace:                  getTrimmedEnv(PresidioNamespace),
		AnalyzerSvcAddress:         getTrimmedEnv(AnalyzerSvcAddress),
		AnonymizerSvcAddress:       getTrimmedEnv(AnonymizerSvcAddress),
		AnonymizerImageSvcAddress:  getTrimmedEnv(AnonymizerImageSvcAddress),
		OcrSvcAddress:              getTrimmedEnv(OcrSvcAddress),
		SchedulerSvcAddress:        getTrimmedEnv(SchedulerSvcAddress),
		RecognizersStoreSvcAddress: getTrimmedEnv(RecognizersStoreSvcAddress),
		APISvcAddress:              getTrimmedEnv(APISvcAddress),
		RedisURL:                   getTrimmedEnv(RedisURL),
		RedisDB:                    viper.GetInt(strings.ToUpper(RedisDb)),
		RedisSSL:                   viper.GetBool(strings.ToUpper(RedisSSL)),
		RedisPassword:              getTrimmedEnv(RedisPassword),
		DatasinkImage:              getTrimmedEnv(DatasinkImageName),
		CollectorImage:             getTrimmedEnv(CollectorImageName),
		DatasinkImagePullPolicy:    getTrimmedEnv(DatasinkImagePullPolicy),
		CollectorImagePullPolicy:   getTrimmedEnv(CollectorImagePullPolicy),
		ScannerRequest:             getTrimmedEnv(ScannerRequest),
		StreamRequest:              getTrimmedEnv(StreamRequest),
		QueueURL:                   getTrimmedEnv(QueueURL),
		LogLevel:                   getTrimmedEnv(LogLevel),
	}

	return &settings
}

func getTrimmedEnv(key string) string {
	return strings.Trim(viper.GetString(strings.ToUpper(key)), " ")
}
