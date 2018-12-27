package cmd

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
)

// isJson returns true if the given string is a valid JSON
func isJSON(s string) bool {
	var js map[string]interface{}
	return json.Unmarshal([]byte(s), &js) == nil
}

// getJSONFileContent reads the content of a given file and if the content is a
// valid JSON returns it
func getJSONFileContent(path string) (string, error) {
	fileContentBytes, err := ioutil.ReadFile(path)
	if err != nil {
		return "", fmt.Errorf("Failed reading file %s", path)
	}
	fileContentStr := string(fileContentBytes)
	isValidJSON := isJSON(fileContentStr)

	if isValidJSON == false {
		errMsg := "The given template file is not a valid json file or does not exists"
		fmt.Println(errMsg)
		return "", fmt.Errorf(errMsg)
	}
	return fileContentStr, nil
}
