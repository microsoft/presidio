package kube

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"k8s.io/client-go/kubernetes/fake"
)

func TestCreateAndDeleteJob(t *testing.T) {

	client := fake.NewSimpleClientset()

	store := &store{
		client:    client,
		namespace: "default",
	}

	name := "jobName"
	image := "imageName"
	commands := []string{"a", "b"}

	// Create job
	err := store.CreateJob(name, image, commands)
	if err != nil {
		t.Fatal(err)
	}

	// List jobs
	jobs, _ := store.ListJobs()
	assert.Equal(t, len(jobs), 1)
	assert.Equal(t, jobs[0], name)

	// Delete job
	err = store.DeleteJob(name)
	if err != nil {
		t.Fatal(err)
	}

	// List jobs
	jobs, _ = store.ListJobs()
	assert.Equal(t, len(jobs), 0)
}
