package kube

import (
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/tools/clientcmd"

	log "github.com/Microsoft/presidio/pkg/logger"
)

// GetClient creates a config from the given master and kubeconfig
// location on disk, then creates a new kubernetes Clientset from that config
func GetClient(master string, kubeConfigPath string) (*kubernetes.Clientset, error) {

	config, err := clientcmd.BuildConfigFromFlags(master, kubeConfigPath)
	if err != nil {
		log.Fatal(err.Error())
	}

	clientset, err := kubernetes.NewForConfig(config)
	if err != nil {
		log.Fatal(err.Error())
	}

	// return the clientset
	return clientset, err
}
