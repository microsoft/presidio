package cmd

import (
	"net/http"

	"github.com/spf13/cobra"

	"github.com/Microsoft/presidio/presctl/cmd/entities"
)

// updateCmd represents the update command
var updateCmd = &cobra.Command{
	Use:   "update",
	Short: "update a specific resource type",
	Long:  `Use this command to update a resource of the specified type.`,
}

var updateTemplateCmd = &cobra.Command{
	Use:   "template",
	Args:  cobra.MinimumNArgs(1),
	Short: "update a template resource",
	Long:  `Use this command to update presidio template.`,
	Run: func(cmd *cobra.Command, args []string) {
		actionName := getFlagValue(cmd, actionFlag)
		path := getFlagValue(cmd, fileFlag)
		projectName := getFlagValue(cmd, projectFlag)
		templateName := args[0]

		fileContentStr, err := getJSONFileContent(path)
		check(err)

		// Send a REST command to presidio instance to update the requested template
		entities.UpdateTemplate(&http.Client{}, projectName, actionName, templateName, fileContentStr)
	},
}

// updateRecognizerCmd represents the custom analysis recognizer update
var updateRecognizerCmd = &cobra.Command{
	Use:   "recognizer",
	Args:  cobra.MinimumNArgs(1),
	Short: "update an existing custom recognizer resource",
	Long:  `Use this command to update an existing custom recognizer resource.`,
	Run: func(cmd *cobra.Command, args []string) {
		path := getFlagValue(cmd, fileFlag)
		recognizerName := args[0]

		fileContentStr, err := getJSONFileContent(path)
		check(err)

		// Send a REST command to presidio instance to create the requested template
		entities.UpdateRecognizer(&http.Client{}, recognizerName, fileContentStr)
	},
}

func init() {
	rootCmd.AddCommand(updateCmd)
	updateCmd.AddCommand(updateTemplateCmd)

	// define supported flags for the add command
	updateTemplateCmd.Flags().StringP(fileFlag, "f", "", "path to a template json file")
	updateTemplateCmd.Flags().String(actionFlag, "", "the requested action. Supported actions: ["+getSupportedActions()+"]")
	updateTemplateCmd.Flags().StringP(projectFlag, "p", "", "project's name")

	// mark flags as required
	updateTemplateCmd.MarkFlagRequired(fileFlag)
	updateTemplateCmd.MarkFlagRequired(actionFlag)
	updateTemplateCmd.MarkFlagRequired(projectFlag)

	updateCmd.AddCommand(updateRecognizerCmd)

	// define supported flags for the add command
	updateRecognizerCmd.Flags().StringP(fileFlag, "f", "", "path to a recognizer json file")

	// mark flags as required
	updateRecognizerCmd.MarkFlagRequired(fileFlag)
}
