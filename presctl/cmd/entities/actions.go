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

// enum of possible actions
const (
	Analyze   = "analyze"
	Anonymize = "anonymize"
)

// ActionMsg defines the structure of the action post body
type ActionMsg struct {
	Text                string
	AnalyzeTemplateID   string
	AnonymizeTemplateID string
}

// AnalyzeOrAnonymize sends a POST REST command to the Presidio instance, to analyze or anonymize text
func AnalyzeOrAnonymize(httpClient httpClient, action string, contentStr string, outputFile string, projectName string) {
	var ip = viper.GetString("presidio_ip")
	var port = viper.GetString("presidio_port")

	url := fmt.Sprintf(actionURLFormat,
		ip,
		port,
		projectName,
		action)

	req, err := http.NewRequest("POST", url, strings.NewReader(contentStr))
	check(err)
	req.Header.Set("Content-Type", "application/json")

	client := httpClient
	response, err := client.Do(req)
	check(err)

	if response.StatusCode != http.StatusOK {
		errMsg := fmt.Sprintf("Operation failed. Returned status code: %d", response.StatusCode)
		fmt.Println(errMsg)
		os.Exit(1)
	}

	body := getBodyString(response)
	if outputFile != "" {
		saveToFile(body, outputFile)
	} else {
		prettyPrintJSON(body)
	}

	fmt.Printf("Success")
}
