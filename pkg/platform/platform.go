package platform

//ContainerDetails
type ContainerDetails struct {
	Name     string
	Image    string
	Commands []string
}

//Store interface
type Store interface {
	PutKVPair(key string, value string) error
	GetKVPair(key string) (string, error)
	DeleteKVPair(key string) error
	CreateJob(name string, image string, commands []string) error
	CreateCronJob(name string, schedule string, containerDetailsArray []ContainerDetails) error
	ListCronJobs() ([]string, error)
	DeleteCronJob(name string) error
	ListJobs() ([]string, error)
	DeleteJob(name string) error
}
