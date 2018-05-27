package consul

import (
	"fmt"

	"github.com/hashicorp/consul/api"

	"github.com/presidium-io/presidium/pkg/logger"
	sd "github.com/presidium-io/presidium/pkg/service-discovery"
)

type consul struct {
	sd *api.Client
}

const tag = "presidium"

//New service discovery store
func New() sd.Store {

	client, err := api.NewClient(api.DefaultConfig())
	if err != nil {
		logger.Fatal(err.Error())
	}
	return &consul{
		sd: client,
	}
}

//Register a service with consul local agent
func (c *consul) Register(name string, address string, port int) error {
	reg := &api.AgentServiceRegistration{
		ID:      name,
		Name:    name,
		Port:    port,
		Address: address,
		Tags:    []string{tag},
	}
	return c.sd.Agent().ServiceRegister(reg)
}

//DeRegister a service with consul local agent
func (c *consul) DeRegister(id string) error {
	return c.sd.Agent().ServiceDeregister(id)
}

//GetService return a service
func (c *consul) GetService(service string) (string, error) {
	passingOnly := true
	addrs, _, err := c.sd.Health().Service(service, tag, passingOnly, nil)
	if len(addrs) == 0 && err == nil {
		err = fmt.Errorf("service ( %s ) was not found", service)
	}
	if err != nil {
		return "", err
	}

	address := fmt.Sprintf("%s:%d", addrs[0].Service.Address, addrs[0].Service.Port)
	return address, nil
}
