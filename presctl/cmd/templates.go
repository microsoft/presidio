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

func saveToFile(response *http.Response, outputFilePath string) {
	body, err := ioutil.ReadAll(response.Body)
	check(err)

	len := response.ContentLength
	bodyStr := string(body[:len])
	file, err := os.Create(outputFilePath)
	check(err)

	defer file.Close()
	unquotedStr, err := strconv.Unquote(bodyStr)
	jsonStr := &bytes.Buffer{}
	if err := json.Indent(jsonStr, []byte(unquotedStr), "", "  "); err != nil {
		os.Exit(1)
	}

	file.WriteString(jsonStr.String())
	check(err)
	fmt.Printf("Template saved to: %s\n", outputFilePath)
}

// createTemplate sends a POST REST command to the Presidio instance, to create the requested template
func templateRestCommand(httpClient httpClient, op restOp, projectName string, actionName string, templateName string, fileContentStr string, outputFilePath string) {
	var ip = viper.GetString("presidio_ip")
	var port = viper.GetString("presidio_port")

	url := fmt.Sprintf(templateURLFormat,
		ip,
		port,
		projectName,
		actionName,
		templateName)

	var restMethod = ""
	if op == update {
		restMethod = "PUT"
	} else if op == create {
		restMethod = "POST"
	} else if op == get {
		restMethod = "GET"
	} else if op == delete {
		restMethod = "DELETE"
	}

	var req *http.Request
	var err error
	if op == create || op == update {
		req, err = http.NewRequest(restMethod, url, strings.NewReader(fileContentStr))
		check(err)
	} else {
		req, err = http.NewRequest(restMethod, url, nil)
		check(err)
	}

	client := httpClient
	response, err := client.Do(req)
	check(err)

	expectedStatusCode := -1
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

	if op == get {
		saveToFile(response, outputFilePath)
	}

	fmt.Printf("Success")
}

func createTemplate(httpClient httpClient, projectName string, actionName string, templateName string, fileContentStr string) {
	templateRestCommand(httpClient, create, projectName, actionName, templateName, fileContentStr, "")
}

func updateTemplate(httpClient httpClient, projectName string, actionName string, templateName string, fileContentStr string) {
	templateRestCommand(httpClient, update, projectName, actionName, templateName, fileContentStr, "")
}

func deleteTemplate(httpClient httpClient, projectName string, actionName string, templateName string) {
	templateRestCommand(httpClient, delete, projectName, actionName, templateName, "", "")
}

func getTemplate(httpClient httpClient, projectName string, actionName string, templateName string, outputFilePath string) {
	templateRestCommand(httpClient, get, projectName, actionName, templateName, "", outputFilePath)
}
