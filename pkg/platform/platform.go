package platform

//Store interface
type Store interface {
	PutKVPair(key string, value string) error
	GetKVPair(key string) (string, error)
	DeleteKVPair(key string) error
	CreateJob(name string, image string, commands []string) error
	ListJobs() ([]string, error)
	DeleteJob(name string) error
}
