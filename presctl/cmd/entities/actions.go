package entities

import (
	"fmt"
	"net/http"
	"os"
	"strings"

	"github.com/spf13/viper"
)

type httpClient interface {
	Do(req *http.Request) (*http.Response, error)
}

// types of possible operations on data
const (
	Analyze   = "analyze"
	Anonymize = "anonymize"
)

// types of jobs available for scheduling
const (
	Scanner = "schedule-scanner-cronjob"
	Stream  = "schedule-streams-job"
)

// ActionMsg defines the structure of the action post body
type ActionMsg struct {
	Text                string
	AnalyzeTemplateID   string
	AnonymizeTemplateID string
}

// restCommand issues an action related REST command to presidio
func restCommand(httpClient httpClient, url string, contentStr string) *http.Response {
	req, err := http.NewRequest("POST", url, strings.NewReader(contentStr))
	check(err)
	req.Header.Set("Content-Type", "application/json")

	client := httpClient
	response, err := client.Do(req)
	check(err)

	return response
}

// actionRestCommand issues an action related REST command to presidio and validates the returned status code
func actionRestCommand(httpClient httpClient, action string, contentStr string, projectName string) *http.Response {
	var ip = viper.GetString("presidio_ip")
	var port = viper.GetString("presidio_port")

	url := fmt.Sprintf(actionURLFormat,
		ip,
		port,
		projectName,
		action)
	response := restCommand(httpClient, url, contentStr)

	if response.StatusCode != http.StatusOK {
		errMsg := fmt.Sprintf("Operation failed. Returned status code: %d", response.StatusCode)
		fmt.Println(errMsg)
		os.Exit(1)
	}

	return response
}

// AnalyzeOrAnonymize sends a POST REST command to the Presidio instance, to analyze or anonymize text
func AnalyzeOrAnonymize(httpClient httpClient, action string, contentStr string, outputFile string, projectName string) {
	response := actionRestCommand(httpClient, action, contentStr, projectName)
	body := getBodyString(response)
	if outputFile != "" {
		saveToFile(body, outputFile)
	} else {
		prettyPrintJSON(body)
	}

	fmt.Printf("Success")
}

// ScheduleJob schedules the different job types
func ScheduleJob(httpClient httpClient, jobType string, projectName string, contentStr string) {
	actionRestCommand(httpClient, jobType, contentStr, projectName)
	fmt.Printf("Success")
}
