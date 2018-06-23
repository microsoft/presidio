package kube

import (
	batchv1 "k8s.io/api/batch/v1"
	"k8s.io/api/batch/v1beta1"
	apiv1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"

	"github.com/Microsoft/presidio/pkg/platform"
)

//CreateJob create k8s job
func (s *store) CreateCronJob(name string, schedule string, containerDetailsArray []platform.ContainerDetails) error {
	jobsClient := s.client.BatchV1beta1().CronJobs(s.namespace)

	var containers []apiv1.Container
	for _, containerDetails := range containerDetailsArray {
		containers = append(containers, apiv1.Container{
			Name:            containerDetails.Name,
			Image:           containerDetails.Image,
			Env:             containerDetails.EnvVars,
			ImagePullPolicy: containerDetails.ImagePullPolicy,
		})
	}

	cronjob := &v1beta1.CronJob{
		ObjectMeta: metav1.ObjectMeta{
			Name: name,
			Labels: map[string]string{
				"app": "presidio",
			},
		},
		Spec: v1beta1.CronJobSpec{
			Schedule:                   schedule,
			SuccessfulJobsHistoryLimit: int32Ptr(5),
			FailedJobsHistoryLimit:     int32Ptr(5),
			JobTemplate: v1beta1.JobTemplateSpec{
				Spec: batchv1.JobSpec{
					BackoffLimit: int32Ptr(5),
					Completions:  int32Ptr(1),
					Template: apiv1.PodTemplateSpec{
						Spec: apiv1.PodSpec{
							Containers:    containers,
							RestartPolicy: "OnFailure",
						},
					},
				},
			},
			ConcurrencyPolicy: v1beta1.ForbidConcurrent,
		},
	}

	_, err := jobsClient.Create(cronjob)
	return err
}

//ListCronJobs list jobs in k8s
func (s *store) ListCronJobs() ([]string, error) {
	names := make([]string, 0)
	jobsClient := s.client.BatchV1beta1().CronJobs(s.namespace)
	list, err := jobsClient.List(metav1.ListOptions{})
	if err != nil {
		return nil, err
	}

	for _, job := range list.Items {
		names = append(names, job.GetName())
	}
	return names, nil
}

//DeleteCronJob deletes the cron job in k8s
func (s *store) DeleteCronJob(name string) error {
	jobsClient := s.client.BatchV1beta1().CronJobs(s.namespace)
	err := jobsClient.Delete(name, &metav1.DeleteOptions{})
	return err
}
