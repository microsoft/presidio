package cmd

import (
	"net/http"

	"github.com/spf13/cobra"

	"github.com/Microsoft/presidio/presctl/cmd/entities"
)

// deleteCmd represents the delete command
var deleteCmd = &cobra.Command{
	Use:   "delete",
	Short: "delete a specific resource type",
	Long:  `Use this command to delete a resource of the specified type.`,
}

var delTemplateCmd = &cobra.Command{
	Use:   "template",
	Args:  cobra.MinimumNArgs(1),
	Short: "delete a template resource",
	Long:  `Use this command to delete a template from presidio.`,
	Run: func(cmd *cobra.Command, args []string) {
		actionName := getFlagValue(cmd, actionFlag)
		projectName := getFlagValue(cmd, projectFlag)
		templateName := args[0]

		// Send a REST command to presidio instance to delete the requested template
		entities.DeleteTemplate(&http.Client{}, projectName, actionName, templateName)
	},
}

// delRecognizerCmd represents the recognizer command
var delRecognizerCmd = &cobra.Command{
	Use:   "recognizer",
	Args:  cobra.MinimumNArgs(1),
	Short: "delete an existing recognizer resource",
	Long:  `Use this command to delete a recognizer.`,
	Run: func(cmd *cobra.Command, args []string) {
		recognizerName := args[0]

		// Send a REST command to presidio instance to get the requested template
		entities.DeleteRecognizer(&http.Client{}, recognizerName)
	},
}

func init() {
	rootCmd.AddCommand(deleteCmd)
	deleteCmd.AddCommand(delTemplateCmd)

	// define supported flags for the del command
	delTemplateCmd.Flags().String(actionFlag, "", "the requested action. Supported actions: ["+getSupportedActions()+"]")
	delTemplateCmd.Flags().StringP(projectFlag, "p", "", "project's name")

	// mark flags as required
	delTemplateCmd.MarkFlagRequired(actionFlag)
	delTemplateCmd.MarkFlagRequired(projectFlag)

	deleteCmd.AddCommand(delRecognizerCmd)
}
