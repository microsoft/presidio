package kube

import (
	"k8s.io/client-go/kubernetes"

	"github.com/Microsoft/presidio/pkg/platform"
)

// store represents a store engine
type store struct {
	client    kubernetes.Interface
	namespace string
}

// New initializes a new storage backend.
func New(namespace string, master string, kubeConfigPath string) (platform.Store, error) {
	c, err := GetClient(master, kubeConfigPath)
	if err != nil {
		return nil, err
	}
	return &store{
		client:    c,
		namespace: namespace,
	}, err
}
