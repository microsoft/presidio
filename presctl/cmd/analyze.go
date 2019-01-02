package cmd

import (
	"encoding/json"
	"net/http"

	"github.com/spf13/cobra"

	"github.com/Microsoft/presidio/presctl/cmd/entities"
)

// analyzeCmd represents the analyze command
var analyzeCmd = &cobra.Command{
	Use:   "analyze",
	Short: "Analyze the given object",
	Long:  `Send the object to Presidio for analysis as described in the templates.`,
	Run: func(cmd *cobra.Command, args []string) {

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
			msg := entities.ActionMsg{Text: queryStr, AnalyzeTemplateID: analyzeTemplateID, AnonymizeTemplateID: anonymizeTemplateID}
			jsonBytes, err = json.Marshal(&msg)
			contentStr = string(jsonBytes)
		} else {
			contentStr, err = getJSONFileContent(path)
		}
		check(err)

		entities.AnalyzeOrAnonymize(&http.Client{}, entities.Analyze, contentStr, outputFile, projectName)
	},
}

func init() {
	rootCmd.AddCommand(analyzeCmd)

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
}
