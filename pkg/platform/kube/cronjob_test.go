package kube

import (
	"testing"

	"github.com/stretchr/testify/assert"
	apiv1 "k8s.io/api/core/v1"
	"k8s.io/client-go/kubernetes/fake"

	"github.com/presid-io/presidio/pkg/platform"
)

func TestCreateAndDeleteCronJob(t *testing.T) {
	client := fake.NewSimpleClientset()

	store := &store{
		client:    client,
		namespace: "default",
	}

	containerDetails := []platform.ContainerDetails{
		{
			EnvVars: []apiv1.EnvVar{
				{Name: "envVar1", Value: "envVarval"},
			},
			Name:  "jobName",
			Image: "imageName",
		},
	}

	jobName := "jobName"
	schedule := "*/1 * * * *"

	// Create job
	err := store.CreateCronJob(jobName, schedule, containerDetails)
	if err != nil {
		t.Fatal(err)
	}

	// List jobs
	jobs, _ := store.ListCronJobs()
	assert.Equal(t, len(jobs), 1)
	assert.Equal(t, jobs[0], jobName)

	// Delete job
	err = store.DeleteCronJob(jobName)
	if err != nil {
		t.Fatal(err)
	}

	// List jobs
	jobs, _ = store.ListCronJobs()
	assert.Equal(t, len(jobs), 0)
}
