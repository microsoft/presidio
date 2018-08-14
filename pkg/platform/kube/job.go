package kube

import (
	batchv1 "k8s.io/api/batch/v1"
	apiv1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"

	"github.com/Microsoft/presidio/pkg/platform"
)

//CreateJob create k8s job
func (s *store) CreateJob(name string, containerDetailsArray []platform.ContainerDetails) error {

	var containers []apiv1.Container
	for _, containerDetails := range containerDetailsArray {
		containers = append(containers, apiv1.Container{
			Name:            containerDetails.Name,
			Image:           containerDetails.Image,
			Env:             containerDetails.EnvVars,
			ImagePullPolicy: containerDetails.ImagePullPolicy,
		})
	}

	jobsClient := s.client.BatchV1().Jobs(s.namespace)
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
					Containers:    containers,
					RestartPolicy: "OnFailure",
				},
			},
		},
	}

	_, err := jobsClient.Create(job)
	return err
}

//ListJobs list jobs in k8s
func (s *store) ListJobs() ([]string, error) {
	names := make([]string, 0)
	jobsClient := s.client.BatchV1().Jobs(s.namespace)
	list, err := jobsClient.List(metav1.ListOptions{})
	if err != nil {
		return nil, err
	}

	for _, job := range list.Items {
		// TODO: add label
		// metadata, err := meta.Accessor(job)
		// if err != nil {
		// 	return nil, err
		// }
		names = append(names, job.GetName())
	}
	return names, nil
}

//DeleteJob delete job in k8s
func (s *store) DeleteJob(name string) error {
	jobsClient := s.client.BatchV1().Jobs(s.namespace)
	err := jobsClient.Delete(name, &metav1.DeleteOptions{})
	return err
}

func int32Ptr(i int32) *int32 { return &i }
