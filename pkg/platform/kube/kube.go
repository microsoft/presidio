package kube

import (
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/kubernetes/fake"

	"github.com/Microsoft/presidio/pkg/platform"
)

// store represents a store engine
type store struct {
	client    kubernetes.Interface
	namespace string
}

// New initializes a new Kubernetes backend.
func New(namespace string, master string) (platform.Store, error) {
	c, err := GetClient(master)
	if err != nil {
		return nil, err
	}
	return &store{
		client:    c,
		namespace: namespace,
	}, err
}

// NewFake initializes a new FAKE Kubernetes backend.
func NewFake() (platform.Store, error) {

	c := fake.NewSimpleClientset()
	return &store{
		client:    c,
		namespace: "default",
	}, nil
}
