package kube

import (
	"testing"

	"github.com/stretchr/testify/assert"
	apiv1 "k8s.io/api/core/v1"

	"github.com/Microsoft/presidio/pkg/platform"
)

func TestCreateAndDeleteCronJob(t *testing.T) {
	store, _ := NewFake()
	containerDetails := []platform.ContainerDetails{
		{
			EnvVars: []apiv1.EnvVar{
				{Name: "envVar1", Value: "envVarval"},
			},
			Name:            "jobName",
			Image:           "imageName",
			ImagePullPolicy: apiv1.PullAlways,
		},
	}

	jobName := "jobName"
	schedule := "*/1 * * * *"

	// Create job
	err := store.CreateCronJob(jobName, schedule, containerDetails)
	assert.NoError(t, err)

	// List jobs
	jobs, _ := store.ListCronJobs()
	assert.Equal(t, len(jobs), 1)
	assert.Equal(t, jobs[0], jobName)

	// Delete job
	err = store.DeleteCronJob(jobName)
	assert.NoError(t, err)

	// List jobs
	jobs, _ = store.ListCronJobs()
	assert.Equal(t, len(jobs), 0)
}
