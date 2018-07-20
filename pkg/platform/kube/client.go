package kube

import (
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/rest"

	log "github.com/presid-io/presidio/pkg/logger"
)

// GetClient creates a config from the given master and kubeconfig
// location on disk, then creates a new kubernetes Clientset from that config
func GetClient() (*kubernetes.Clientset, error) {

	config, err := rest.InClusterConfig()
	if err != nil {
		log.Fatal(err.Error())
	}

	// creates the clientset
	return kubernetes.NewForConfig(config)
}
