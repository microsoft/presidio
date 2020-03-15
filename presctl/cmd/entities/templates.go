package entities

import (
	"fmt"
)

const templateURLFormat = "http://%s:%s/api/v1/templates/%s/%s/%s"

func constructTemplateURL(projectName string, actionName string, templateName string) string {
	var ip, port = GetIPPort()

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
