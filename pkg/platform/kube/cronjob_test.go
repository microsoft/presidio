package kube

import (
	"fmt"
	"testing"

	"github.com/robfig/cron"
	"github.com/stretchr/testify/assert"
	"k8s.io/client-go/kubernetes/fake"
)

func TestCreateAndDeleteCronJob(t *testing.T) {

	client := fake.NewSimpleClientset()

	c := cron.NewParser(cron.Minute | cron.Hour | cron.Dom | cron.Month | cron.Dow | cron.Descriptor)
	schecule, err := c.Parse("@every 1h30m")
	fmt.Print(schecule)
	fmt.Print(err.Error())

	store := &store{
		client:    client,
		namespace: "default",
	}

	containerDetails := []ContainerDetails{
		ContainerDetails{
			Commands: []string{"a", "b"},
			Name:     "jobName",
			Image:    "imageName",
		},
	}

	jobName := "jobName"
	schedule := "*/1 * * * *"

	// Create job
	err = store.CreateCronJob(jobName, schedule, containerDetails)
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
