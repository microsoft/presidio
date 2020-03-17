package entities

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
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
	Scanner   = "schedule-scanner-cronjob"
	Stream    = "schedule-streams-job"
)

const (
	create = 0
	update = 1
	delete = 2
	get    = 3
)

type restOp int

// ActionMsg defines the structure of the action post body
type ActionMsg struct {
	Text                string
	AnalyzeTemplateID   string
	AnonymizeTemplateID string
}

// GetIPPort returns both the Presidio IP and Port from the viper configuration
func GetIPPort() (string, string) {
	var ip = viper.GetString("presidio_ip")
	var port = viper.GetString("presidio_port")
	return ip, port
}

// if error is not null print it and exit the program
func check(err error) {
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
}

// getBodyString returns the response's body
func getBodyString(response *http.Response) string {
	body, err := ioutil.ReadAll(response.Body)
	check(err)

	len := response.ContentLength
	bodyStr := string(body[:len])

	return bodyStr
}

// saveToFile saves the given json in a indented manner to a file
func saveToFile(jsonBody string, outputFilePath string) {
	jsonStr := prettifyJSON(jsonBody)
	file, err := os.Create(outputFilePath)
	check(err)
	_, err = file.WriteString(jsonStr)
	defer file.Close()
	check(err)
	fmt.Printf("Template saved to: %s\n", outputFilePath)
}

// prettifyJSON makes a valid json string 'pretty' (human readable / indented)
func prettifyJSON(body string) string {
	jsonStr := &bytes.Buffer{}
	err := json.Indent(jsonStr, []byte(body), "", "  ")
	check(err)
	return jsonStr.String()
}

// prettyPrintJSON prints the given json in an indented manner
func prettyPrintJSON(jsonBody string) {
	jsonStr := prettifyJSON(jsonBody)
	fmt.Printf("Result: %s\n", jsonStr)
}

// restCommand sends a REST command to the Presidio cluster in order to manage resources
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
	default:
		errMsg := fmt.Sprintf("Unknown operation code %d", op)
		fmt.Println(errMsg)
		os.Exit(1)
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

	// getBodyString can be called only once, so we save it into a var
	res := getBodyString(response)
	if res != "" {
		if outputFilePath != "" {
			saveToFile(res, outputFilePath)
		} else {
			prettyPrintJSON(res)
		}
	}

	fmt.Println("Success")
}
