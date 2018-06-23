package local

import (
	"fmt"

	"github.com/Microsoft/presidio/pkg/platform"
)

func (s *store) CreateJob(name string, containerDetailsArray []platform.ContainerDetails) error {
	return fmt.Errorf("Not implemented")
}

func (s *store) CreateCronJob(name string, schedule string, containerDetailsArray []platform.ContainerDetails) error {
	return fmt.Errorf("Not implemented")
}

func (s *store) ListJobs() ([]string, error) {
	return nil, fmt.Errorf("Not implemented")
}

func (s *store) ListCronJobs() ([]string, error) {
	return nil, fmt.Errorf("Not implemented")
}

func (s *store) DeleteJob(name string) error {
	return fmt.Errorf("Not implemented")
}

func (s *store) DeleteCronJob(name string) error {
	return fmt.Errorf("Not implemented")
}
