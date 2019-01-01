package cmd

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"strconv"
	"strings"

	"github.com/spf13/viper"
)

const templateURLFormat = "http://%s:%s/api/v1/templates/%s/%s/%s"
const actionURLFormat = "http://%s:%s/api/v1/projects/%s/%s"

const (
	create = 0
	update = 1
	delete = 2
	get    = 3
)

type restOp int

func check(err error) {
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
}

func getBodyString(response *http.Response) string {
	body, err := ioutil.ReadAll(response.Body)
	check(err)

	len := response.ContentLength
	bodyStr := string(body[:len])

	return bodyStr
}
func prettifyJSON(body string) string {
	jsonStr := &bytes.Buffer{}
	err := json.Indent(jsonStr, []byte(body), "", "  ")
	check(err)
	return jsonStr.String()
}

func prettyPrintJSON(jsonBody string) {
	jsonStr := prettifyJSON(jsonBody)
	fmt.Printf("Result: %s\n", jsonStr)
}

func saveToFile(jsonBody string, outputFilePath string) {
	jsonStr := prettifyJSON(jsonBody)
	file, err := os.Create(outputFilePath)
	check(err)
	_, err = file.WriteString(jsonStr)
	defer file.Close()
	check(err)
	fmt.Printf("Template saved to: %s\n", outputFilePath)
}

// templateRestCommand sends a POST REST command to the Presidio instance in order to manage templates
func templateRestCommand(httpClient httpClient, op restOp, projectName string, actionName string, templateName string, fileContentStr string, outputFilePath string) {
	var ip = viper.GetString("presidio_ip")
	var port = viper.GetString("presidio_port")

	url := fmt.Sprintf(templateURLFormat,
		ip,
		port,
		projectName,
		actionName,
		templateName)

	var req *http.Request
	var err error
	switch op {
	case create:
		req, err = http.NewRequest("POST", url, strings.NewReader(fileContentStr))
	case update:
		req, err = http.NewRequest("PUT", url, strings.NewReader(fileContentStr))
	case delete:
		req, err = http.NewRequest("DELETE", url, nil)
	case get:
		req, err = http.NewRequest("GET", url, nil)
	}
	check(err)

	client := httpClient
	response, err := client.Do(req)
	check(err)

	var expectedStatusCode int
	if op == create {
		expectedStatusCode = http.StatusCreated
	} else if op == delete {
		expectedStatusCode = http.StatusNoContent
	} else {
		expectedStatusCode = http.StatusOK
	}

	if response.StatusCode != expectedStatusCode {
		errMsg := fmt.Sprintf("Operation failed. Returned status code: %d",
			response.StatusCode)
		fmt.Println(errMsg)
		os.Exit(1)
	}

	if op != get {
		fmt.Printf("Success")
		return
	}

	unquotedStr, err := strconv.Unquote(getBodyString(response))
	check(err)
	if outputFilePath != "" {
		saveToFile(unquotedStr, outputFilePath)
	} else {
		prettyPrintJSON(unquotedStr)
	}

	fmt.Printf("Success")
}

// createTemplate creates a new template
func createTemplate(httpClient httpClient, projectName string, actionName string, templateName string, fileContentStr string) {
	templateRestCommand(httpClient, create, projectName, actionName, templateName, fileContentStr, "")
}

// updateTemplate updates an existing template
func updateTemplate(httpClient httpClient, projectName string, actionName string, templateName string, fileContentStr string) {
	templateRestCommand(httpClient, update, projectName, actionName, templateName, fileContentStr, "")
}

// deleteTemplate deletes an existing template
func deleteTemplate(httpClient httpClient, projectName string, actionName string, templateName string) {
	templateRestCommand(httpClient, delete, projectName, actionName, templateName, "", "")
}

// getTemplate retrieved an existing template, can be logged or saved to a file
func getTemplate(httpClient httpClient, projectName string, actionName string, templateName string, outputFilePath string) {
	templateRestCommand(httpClient, get, projectName, actionName, templateName, "", outputFilePath)
}
