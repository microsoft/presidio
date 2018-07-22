package local

import (
	"errors"
)

func (s *store) CreateJob(name string, image string, commands []string) error {
	return errors.New("Not implemented")
}

func (s *store) ListJobs() ([]string, error) {
	return nil, errors.New("Not implemented")
}

func (s *store) DeleteJob(name string) error {
	return errors.New("Not implemented")
}
