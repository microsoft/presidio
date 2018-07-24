package kube

import (
	batchv1 "k8s.io/api/batch/v1"
	"k8s.io/api/batch/v1beta1"
	apiv1 "k8s.io/api/core/v1"
	"k8s.io/apimachinery/pkg/api/meta"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

//CreateJob create k8s job
func (s *store) CreateCronJob(name string, image string, schedule string, commands []string) error {
	jobsClient := s.client.BatchV1beta1().CronJobs(s.namespace)

	cronjob := &v1beta1.CronJob{
		ObjectMeta: metav1.ObjectMeta{
			Name: name,
		},
		Spec: v1beta1.CronJobSpec{
			Schedule: schedule,
			JobTemplate: v1beta1.JobTemplateSpec{
				ObjectMeta: metav1.ObjectMeta{
					Labels: map[string]string{
						"app": "presidio",
					},
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
			},
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
		metadata, err := meta.Accessor(job)
		if err != nil {
			return nil, err
		}
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
