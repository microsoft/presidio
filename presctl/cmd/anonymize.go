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
	Short: "Anonymize the given text",
	Long:  `Send the text to Presidio for anonymization according to the specified template.`,
	Run: func(cmd *cobra.Command, args []string) {
		analyzeTemplateID := getFlagValue(cmd, analyzeTemplateIDFlag)
		anonymizeTemplateID := getFlagValue(cmd, anonymizeTemplateIDFlag)
		outputFile := getFlagValue(cmd, outputFlag)
		path := getFlagValue(cmd, fileFlag)
		projectName := getFlagValue(cmd, projectFlag)
		queryStr := getFlagValue(cmd, stringFlag)

		// currently there is no way to define a 'group' of required params in cobra
		// we want to either have a valid anonymize request payload OR an anonymize template
		// id, analyze template id and inline text for anonymization
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
	anonymizeCmd.Flags().StringP(fileFlag, "f", "", "path to an anonymize request json file")
	anonymizeCmd.Flags().StringP(stringFlag, "s", "", "string to analyze")
	anonymizeCmd.Flags().StringP(projectFlag, "p", "", "project's name")
	anonymizeCmd.Flags().StringP(outputFlag, "o", "", "output file path")
	anonymizeCmd.Flags().StringP(analyzeTemplateIDFlag, "l", "", "the analyze templateId")
	anonymizeCmd.Flags().StringP(anonymizeTemplateIDFlag, "m", "", "the anonymize templateId")

	// mark flag as required
	anonymizeCmd.MarkFlagRequired(projectFlag)
}
