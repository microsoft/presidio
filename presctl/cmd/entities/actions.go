package entities

import (
	"fmt"
	"net/http"
	"os"
	"strconv"
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
	Scanner   = "schedule-scanner-cronjob"
	Stream    = "schedule-streams-job"
)

// ActionMsg defines the structure of the action post body
type ActionMsg struct {
	Text                string
	AnalyzeTemplateID   string
	AnonymizeTemplateID string
}

// restCommand sends a POST REST command to the Presidio instance in order to manage resources
func restCommand(httpClient httpClient, op restOp, url string, fileContentStr string, outputFilePath string) {
	var req *http.Request
	var err error
	switch op {
	case create:
		req, err = http.NewRequest("POST", url, strings.NewReader(fileContentStr))
		req.Header.Set("Content-Type", "application/json")
	case update:
		req, err = http.NewRequest("PUT", url, strings.NewReader(fileContentStr))
		req.Header.Set("Content-Type", "application/json")
	case delete:
		req, err = http.NewRequest("DELETE", url, nil)
	case get:
		req, err = http.NewRequest("GET", url, nil)
	}
	check(err)

	response, err := httpClient.Do(req)
	check(err)

	if response.StatusCode >= 300 {
		errMsg := fmt.Sprintf("Operation failed. Returned status code: %d",
			response.StatusCode)
		fmt.Println(errMsg)
		os.Exit(1)
	}

	if op != get {
		fmt.Println("Success")
		return
	}

	fmt.Println(getBodyString(response))

	unquotedStr, err := strconv.Unquote(getBodyString(response))
	check(err)
	if outputFilePath != "" {
		saveToFile(unquotedStr, outputFilePath)
	} else {
		prettyPrintJSON(unquotedStr)
	}

	fmt.Println("Success")
}

// actionRestCommand issues an action related REST command to presidio and validates the returned status code
func actionRestCommand(httpClient httpClient, action string, contentStr string, projectName string) {
	var ip = viper.GetString("presidio_ip")
	var port = viper.GetString("presidio_port")

	url := fmt.Sprintf(actionURLFormat,
		ip,
		port,
		projectName,
		action)
	restCommand(httpClient, create, url, contentStr, "")
}

// AnalyzeOrAnonymize sends a POST REST command to the Presidio instance, to analyze or anonymize text
func AnalyzeOrAnonymize(httpClient httpClient, action string, contentStr string, outputFile string, projectName string) {
	actionRestCommand(httpClient, action, contentStr, projectName)
}

// ScheduleJob schedules the different job types
func ScheduleJob(httpClient httpClient, jobType string, projectName string, contentStr string) {
	actionRestCommand(httpClient, jobType, contentStr, projectName)
}
