package sd

//Store interface
type Store interface {
	// Get a Service
	GetService(service string) (string, error)
	// Register a service with local agent
	Register(name string, address string, port int) error
	// DeRegister a service with local agent
	DeRegister(id string) error
}
