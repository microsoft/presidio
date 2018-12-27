package main

import (
	"os"

	"github.com/stretchr/testify/assert"

	types "github.com/Microsoft/presidio-genproto/golang"

	"github.com/Microsoft/presidio/pkg/platform"

	"testing"

	"github.com/Microsoft/presidio/pkg/platform/kube"
)

func TestMain(m *testing.M) {
	os.Setenv("DATASINK_GRPC_PORT", "5000")
	os.Setenv("REDIS_URL", "fake_redis")
	os.Setenv("ANALYZER_SVC_ADDRESS", "fake_anaylzer")
	os.Setenv("ANONYMIZER_SVC_ADDRESS", "fake_anonymizer")
	os.Setenv("DATASINK_IMAGE_PULL_POLICY", "Always")
	os.Setenv("COLLECTOR_IMAGE_PULL_POLICY", "Always")
	settings = platform.GetSettings()
	os.Exit(m.Run())
}

func TestCreateScannerJob(t *testing.T) {

	store, _ = kube.NewFake()

	r := &types.ScannerCronJobRequest{}
	r.ScanRequest = &types.ScanRequest{}
	r.Name = "test"
	r.Trigger = &types.Trigger{
		Schedule: &types.Schedule{
			RecurrencePeriod: "0:0:0:0",
		},
	}
	_, err := applyScanRequest(r)
	assert.NoError(t, err)

	l, err := store.ListCronJobs()
	assert.NoError(t, err)

	assert.Equal(t, 1, len(l))
}

func TestCreateStreamJob(t *testing.T) {

	store, _ = kube.NewFake()

	r := &types.StreamsJobRequest{}
	r.StreamsRequest = &types.StreamRequest{}
	r.Name = "test"
	r.StreamsRequest.StreamConfig = &types.StreamConfig{
		PartitionCount: 32,
	}
	_, err := applyStreamRequest(r)
	assert.NoError(t, err)

	l, err := store.ListJobs()
	assert.NoError(t, err)

	assert.Equal(t, r.StreamsRequest.StreamConfig.PartitionCount, int32(len(l)))
}
