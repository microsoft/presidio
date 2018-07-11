package job

import (
	"fmt"

	batchv1 "k8s.io/api/batch/v1"
	apiv1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"

	"github.com/presid-io/presidio/pkg/logger"

	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/rest"
)

var clientset *kubernetes.Clientset

func init() {
	// creates the in-cluster config
	config, err := rest.InClusterConfig()
	if err != nil {
		panic(err.Error())
	}
	// creates the clientset
	clientset, err = kubernetes.NewForConfig(config)
	if err != nil {
		logger.Fatal(err.Error())
	}
}

//CreateJob create k8s job
func CreateJob(namespace string, name string, image string, commands []string) {
	jobsClient := clientset.BatchV1().Jobs(namespace)

	job := &batchv1.Job{
		ObjectMeta: metav1.ObjectMeta{
			Name: name,
		},
		Spec: batchv1.JobSpec{
			BackoffLimit: int32Ptr(5),
			Template: apiv1.PodTemplateSpec{
				ObjectMeta: metav1.ObjectMeta{
					Labels: map[string]string{
						"app": "presidio",
					},
				},
				Spec: apiv1.PodSpec{
					Containers: []apiv1.Container{
						{
							Name:    name,
							Image:   image,
							Command: commands,
						},
					},
					RestartPolicy: "never",
				},
			},
		},
	}

	result, err := jobsClient.Create(job)
	if err != nil {
		panic(err)
	}
	logger.Info(fmt.Sprintf("Created job %q.\n", result.GetObjectMeta().GetName()))

}

//ListJobs list jobs in k8s
func ListJobs(namespace string) (*batchv1.JobList, error) {
	jobsClient := clientset.BatchV1().Jobs(namespace)
	list, err := jobsClient.List(metav1.ListOptions{})
	if err != nil {
		return nil, err
	}
	return list, nil
}

//DeleteJob delete job in k8s
func DeleteJob(namespace string, name string) error {
	jobsClient := clientset.BatchV1().Jobs(namespace)
	err := jobsClient.Delete(name, &metav1.DeleteOptions{})
	if err != nil {
		return err
	}
	logger.Info(fmt.Sprintf("Deleted job %s", name))
	return nil
}

func int32Ptr(i int32) *int32 { return &i }
