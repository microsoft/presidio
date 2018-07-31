package platform

import apiv1 "k8s.io/api/core/v1"

//ContainerDetails ...
type ContainerDetails struct {
	Name    string
	Image   string
	EnvVars []apiv1.EnvVar
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
