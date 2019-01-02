package cmd

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"

	"github.com/spf13/cobra"

	"github.com/Microsoft/presidio/presctl/cmd/entities"
)

// anonymizeCmd represents the anonymize command
var anonymizeCmd = &cobra.Command{
	Use:   "anonymize",
	Short: "Anonymize the given object",
	Long:  `Send the object to Presidio for anonymization as described in the templates.`,
	Run: func(cmd *cobra.Command, args []string) {
		analyzeTemplateID := getFlagValue(cmd, analyzeTemplateIDFlag)
		anonymizeTemplateID := getFlagValue(cmd, anonymizeTemplateIDFlag)
		outputFile := getFlagValue(cmd, outputFlag)
		path := getFlagValue(cmd, fileFlag)
		projectName := getFlagValue(cmd, projectFlag)
		queryStr := getFlagValue(cmd, stringFlag)

		// currently there is no way to define a 'group' if required params in cobra
		if path == "" && (queryStr == "" || analyzeTemplateID == "" || anonymizeTemplateID == "") {
			fmt.Printf("must supply the '%s' flag or the '%s', %s' and '%s' flags", fileFlag, stringFlag, analyzeTemplateIDFlag, anonymizeTemplateIDFlag)
			os.Exit(1)
		}

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

		entities.AnalyzeOrAnonymize(&http.Client{}, entities.Anonymize, contentStr, outputFile, projectName)
	},
}

func init() {
	rootCmd.AddCommand(anonymizeCmd)

	// define supported flags for the analyze command
	anonymizeCmd.Flags().StringP(fileFlag, "f", "", "path to a template json file")
	anonymizeCmd.Flags().StringP(stringFlag, "s", "", "string to analyze")
	anonymizeCmd.Flags().String(projectFlag, "", "project's name")
	anonymizeCmd.Flags().StringP(outputFlag, "o", "", "output file path")
	anonymizeCmd.Flags().String(analyzeTemplateIDFlag, "", "the analyze templateId")
	anonymizeCmd.Flags().String(anonymizeTemplateIDFlag, "", "the anonymize templateId")

	// mark flags as required
	anonymizeCmd.MarkFlagRequired(projectFlag)
}
