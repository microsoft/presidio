package platform

import (
	log "github.com/Microsoft/presidio/pkg/logger"

	apiv1 "k8s.io/api/core/v1"
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
	CreateJob(name string, image string, commands []string) error
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
