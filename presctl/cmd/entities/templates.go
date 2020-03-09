package entities

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"

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

func constructTemplateURL(projectName string, actionName string, templateName string) string {
	var ip = viper.GetString("presidio_ip")
	var port = viper.GetString("presidio_port")

	return fmt.Sprintf(templateURLFormat,
		ip,
		port,
		projectName,
		actionName,
		templateName)
}

// CreateTemplate creates a new recognizer
func CreateTemplate(httpClient httpClient, projectName string, actionName string, templateName string, fileContentStr string) {
	url := constructTemplateURL(projectName, actionName, templateName)
	restCommand(httpClient, create, url, fileContentStr, "")
}

// UpdateTemplate updates an existing recognizer
func UpdateTemplate(httpClient httpClient, projectName string, actionName string, templateName string, fileContentStr string) {
	url := constructTemplateURL(projectName, actionName, templateName)
	restCommand(httpClient, update, url, fileContentStr, "")
}

// DeleteTemplate deletes an existing recognizer
func DeleteTemplate(httpClient httpClient, projectName string, actionName string, templateName string) {
	url := constructTemplateURL(projectName, actionName, templateName)
	restCommand(httpClient, delete, url, "", "")
}

// GetTemplate retrieved an existing recognizer, can be logged or saved to a file
func GetTemplate(httpClient httpClient, projectName string, actionName string, templateName string, outputFilePath string) {
	url := constructTemplateURL(projectName, actionName, templateName)
	restCommand(httpClient, get, url, "", outputFilePath)
}
