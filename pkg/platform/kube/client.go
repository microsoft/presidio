package kube

import (
	"os"

	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/tools/clientcmd"

	log "github.com/Microsoft/presidio/pkg/logger"
)

const (
	envKubeConfig = "KUBECONFIG"
)

// GetClient creates a config from the given master and kubeconfig
// location on disk, then creates a new kubernetes Clientset from that config
func GetClient(master string) (*kubernetes.Clientset, error) {

	kubeConfigPath := kubeConfigPath()
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

func kubeConfigPath() string {
	if v, ok := os.LookupEnv(envKubeConfig); ok {
		return v
	}
	defConfig := os.ExpandEnv("$HOME/.kube/config")
	if _, err := os.Stat(defConfig); err == nil {
		log.Info("Using config from " + defConfig)
		return defConfig
	}

	return ""
}
