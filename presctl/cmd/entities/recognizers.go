package entities

import (
	"fmt"
)

const recognizerURLFormat = "http://%s:%s/api/v1/analyzer/recognizers/%s"

func constructRecognizerURL(recognizerName string) string {
	var ip, port = GetIPPort()

	return fmt.Sprintf(recognizerURLFormat,
		ip,
		port,
		recognizerName)
}

// CreateRecognizer creates a new recognizer
func CreateRecognizer(httpClient httpClient, name string, fileContentStr string) {
	url := constructRecognizerURL(name)
	restCommand(httpClient, create, url, fileContentStr, "")
}

// UpdateRecognizer updates an existing recognizer
func UpdateRecognizer(httpClient httpClient, name string, fileContentStr string) {
	url := constructRecognizerURL(name)
	restCommand(httpClient, update, url, fileContentStr, "")
}

// DeleteRecognizer deletes an existing recognizer
func DeleteRecognizer(httpClient httpClient, name string) {
	url := constructRecognizerURL(name)
	restCommand(httpClient, delete, url, "", "")
}

// GetRecognizer retrieved an existing recognizer, can be logged or saved to a file
func GetRecognizer(httpClient httpClient, name string, outputFilePath string) {
	url := constructRecognizerURL(name)
	restCommand(httpClient, get, url, "", outputFilePath)
}
