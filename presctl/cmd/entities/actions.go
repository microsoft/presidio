package entities

import (
	"fmt"

	"github.com/spf13/viper"
)

const actionURLFormat = "http://%s:%s/api/v1/projects/%s/%s"

// actionRestCommand issues an action related REST command to presidio and validates the returned status code
func constructActionURL(action string, contentStr string, projectName string) string {
	var ip = viper.GetString("presidio_ip")
	var port = viper.GetString("presidio_port")

	return fmt.Sprintf(actionURLFormat,
		ip,
		port,
		projectName,
		action)
}

// AnalyzeOrAnonymize sends a POST REST command to the Presidio instance, to analyze or anonymize text
func AnalyzeOrAnonymize(httpClient httpClient, action string, contentStr string, outputFile string, projectName string) {
	url := constructActionURL(action, contentStr, projectName)
	restCommand(httpClient, create, url, contentStr, "")
}

// ScheduleJob schedules the different job types
func ScheduleJob(httpClient httpClient, jobType string, projectName string, contentStr string) {
	url := constructActionURL(jobType, contentStr, projectName)
	restCommand(httpClient, create, url, contentStr, "")
}
