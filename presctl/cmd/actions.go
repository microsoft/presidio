package cmd

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"strings"

	"github.com/spf13/cobra"
	"github.com/spf13/viper"
)

const (
	analyze   = "analyze"
	anonymize = "anonymize"
)

// analyzeCmd represents the analyze command
var analyzeCmd = &cobra.Command{
	Use:   "analyze",
	Short: "Analyze the given object",
	Long:  `Send the object to Presidio for analysis as described in the templates.`,
	Run: func(cmd *cobra.Command, args []string) {
		analyzeOrAnonymize(&http.Client{}, analyze, cmd)
	},
}

// anonymizeCmd represents the anonymize command
var anonymizeCmd = &cobra.Command{
	Use:   "anonymize",
	Short: "Anonymize the given object",
	Long:  `Send the object to Presidio for anonymization as described in the templates.`,
	Run: func(cmd *cobra.Command, args []string) {
		analyzeOrAnonymize(&http.Client{}, anonymize, cmd)
	},
}

type actionMsg struct {
	Text                string
	AnalyzeTemplateID   string
	AnonymizeTemplateID string
}

// analyzeOrAnonymize sends a POST REST command to the Presidio instance, to analyze or anonymize text
func analyzeOrAnonymize(httpClient httpClient, action string, cmd *cobra.Command) {
	var ip = viper.GetString("presidio_ip")
	var port = viper.GetString("presidio_port")

	analyzeTemplateID := getFlagValue(cmd, analyzeTemplateIDFlag)
	anonymizeTemplateID := getFlagValue(cmd, anonymizeTemplateIDFlag)
	outputFile := getFlagValue(cmd, outputFlag)
	path := getFlagValue(cmd, fileFlag)
	projectName := getFlagValue(cmd, projectFlag)
	queryStr := getFlagValue(cmd, stringFlag)

	// either create a json body from the given params, or send a given json file
	var contentStr string
	var err error
	var jsonBytes []byte
	if path == "" {
		msg := actionMsg{queryStr, analyzeTemplateID, anonymizeTemplateID}
		jsonBytes, err = json.Marshal(&msg)
		contentStr = string(jsonBytes)
	} else {
		contentStr, err = getJSONFileContent(path)
	}
	check(err)

	url := fmt.Sprintf(actionURLFormat,
		ip,
		port,
		projectName,
		action)

	var req *http.Request
	req, err = http.NewRequest("POST", url, strings.NewReader(contentStr))
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

func init() {
	rootCmd.AddCommand(analyzeCmd)
	rootCmd.AddCommand(anonymizeCmd)

	// define supported flags for the analyze command
	analyzeCmd.Flags().StringP(fileFlag, "f", "", "path to a template json file")
	analyzeCmd.Flags().String(projectFlag, "", "project's name")
	analyzeCmd.Flags().StringP(outputFlag, "o", "", "output file path")
	analyzeCmd.Flags().StringP(stringFlag, "s", "", "string to analyze")
	analyzeCmd.Flags().String(analyzeTemplateIDFlag, "", "the analyze templateId")
	analyzeCmd.Flags().String(anonymizeTemplateIDFlag, "", "the anonymize templateId")

	// mark flags as required
	analyzeCmd.MarkFlagRequired(projectFlag)
	// todo: make f or s mandatory but not both...

	// define supported flags for the analyze command
	anonymizeCmd.Flags().StringP(fileFlag, "f", "", "path to a template json file")
	anonymizeCmd.Flags().StringP(stringFlag, "s", "", "string to analyze")
	anonymizeCmd.Flags().String(projectFlag, "", "project's name")
	anonymizeCmd.Flags().StringP(outputFlag, "o", "", "output file path")
	anonymizeCmd.Flags().String(analyzeTemplateIDFlag, "", "the analyze templateId")
	anonymizeCmd.Flags().String(anonymizeTemplateIDFlag, "", "the anonymize templateId")

	// mark flags as required
	anonymizeCmd.MarkFlagRequired(projectFlag)
	// todo: make f or s mandatory but not both...
}
