package platform

import (
	"os"
	"testing"

	"github.com/stretchr/testify/assert"
)

func addSpaces(key string) string {
	return "  " + key + "  "
}

func TestMain(t *testing.T) {

	// Expected values
	var analyzerSvcAddress = "fake_AnalyzerSvcAddress"
	var anonymizerSvcAddress = "fake_AnonymizerSvcAddress"
	var collectorImage = "fake_CollectorImage"
	var collectorImagePullPolicy = "fake_CollectorImagePullPolicy"
	var datasinkGrpcPort = "1234"
	var datasinkImage = "fake_DatasinkImage"
	var datasinkImagePullPolicy = "fake_DatasinkImagePullPolicy"
	var grpcPort = "1234"
	var namespace = "fake_Namespace"
	var queueURL = "fake_QueueURL"
	var redisURL = "fake_RedisURL"
	var scannerRequest = "fake_ScannerRequest"
	var schedulerSvcAddress = "fake_SchedulerSvcAddress"
	var streamRequest = "fake_StreamRequest"
	var webPort = "1234"

	os.Setenv("ANALYZER_SVC_ADDRESS", addSpaces(analyzerSvcAddress))
	os.Setenv("ANONYMIZER_SVC_ADDRESS", addSpaces(anonymizerSvcAddress))
	os.Setenv("COLLECTOR_IMAGE_NAME", addSpaces(collectorImage))
	os.Setenv("COLLECTOR_IMAGE_PULL_POLICY", addSpaces(collectorImagePullPolicy))
	os.Setenv("DATASINK_IMAGE_NAME", addSpaces(datasinkImage))
	os.Setenv("DATASINK_IMAGE_PULL_POLICY", addSpaces(datasinkImagePullPolicy))
	os.Setenv("DATASINK_GRPC_PORT", addSpaces(datasinkGrpcPort))
	os.Setenv("GRPC_PORT", addSpaces(grpcPort))
	os.Setenv("PRESIDIO_NAMESPACE", addSpaces(namespace))
	os.Setenv("QUEUE_URL", addSpaces(queueURL))
	os.Setenv("REDIS_URL", addSpaces(redisURL))
	os.Setenv("SCANNER_REQUEST", addSpaces(scannerRequest))
	os.Setenv("SCHEDULER_SVC_ADDRESS", addSpaces(schedulerSvcAddress))
	os.Setenv("STREAM_REQUEST", addSpaces(streamRequest))
	os.Setenv("WEB_PORT", addSpaces(webPort))

	// Get settings
	var settings = GetSettings()

	// All should be trimmed
	assert.Equal(t, settings.AnalyzerSvcAddress, analyzerSvcAddress)
	assert.Equal(t, settings.AnonymizerSvcAddress, anonymizerSvcAddress)
	assert.Equal(t, settings.CollectorImage, collectorImage)
	assert.Equal(t, settings.CollectorImagePullPolicy, collectorImagePullPolicy)
	assert.Equal(t, settings.DatasinkGrpcPort, datasinkGrpcPort)
	assert.Equal(t, settings.DatasinkImage, datasinkImage)
	assert.Equal(t, settings.DatasinkImagePullPolicy, datasinkImagePullPolicy)
	assert.Equal(t, settings.GrpcPort, grpcPort)
	assert.Equal(t, settings.Namespace, namespace)
	assert.Equal(t, settings.QueueURL, queueURL)
	assert.Equal(t, settings.RedisURL, redisURL)
	assert.Equal(t, settings.ScannerRequest, scannerRequest)
	assert.Equal(t, settings.SchedulerSvcAddress, schedulerSvcAddress)
	assert.Equal(t, settings.StreamRequest, streamRequest)
	assert.Equal(t, settings.WebPort, webPort)
}
