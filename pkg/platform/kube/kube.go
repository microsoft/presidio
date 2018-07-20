package kube

import (
	"k8s.io/client-go/kubernetes"

	"github.com/presid-io/presidio/pkg/platform"
)

// store represents a store engine
type store struct {
	client    kubernetes.Interface
	namespace string
}

// New initializes a new storage backend.
func New(namespace string) (platform.Store, error) {
	c, err := GetClient()
	if err == nil {
		return nil, err
	}
	return &store{
		client:    c,
		namespace: namespace,
	}, err
}
