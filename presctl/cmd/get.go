package cmd

import (
	"net/http"

	"github.com/spf13/cobra"

	"github.com/Microsoft/presidio/presctl/cmd/entities"
)

// getCmd represents the get command
var getCmd = &cobra.Command{
	Use:   "get",
	Short: "get a specific resource type",
	Long:  `Use this command to get a resource of the specified type.`,
}

// templateCmd represents the template command
var getTemplateCmd = &cobra.Command{
	Use:   "template",
	Args:  cobra.MinimumNArgs(1),
	Short: "gets an existing template resource",
	Long:  `Use this command to get a template.`,
	Run: func(cmd *cobra.Command, args []string) {
		actionName := getFlagValue(cmd, actionFlag)
		outputFile := getFlagValue(cmd, outputFlag)
		projectName := getFlagValue(cmd, projectFlag)
		templateName := args[0]

		// Send a REST command to presidio instance to get the requested template
		entities.GetTemplate(&http.Client{}, projectName, actionName, templateName, outputFile)
	},
}

// getRecognizerCmd represents the recognizer command
var getRecognizerCmd = &cobra.Command{
	Use:   "recognizer",
	Args:  cobra.MinimumNArgs(1),
	Short: "gets an existing recognizer resource",
	Long:  `Use this command to get a recognizer.`,
	Run: func(cmd *cobra.Command, args []string) {
		outputFile := getFlagValue(cmd, outputFlag)
		recognizerName := args[0]

		// Send a REST command to presidio instance to get the requested template
		entities.GetRecognizer(&http.Client{}, recognizerName, outputFile)
	},
}

func init() {
	rootCmd.AddCommand(getCmd)
	getCmd.AddCommand(getTemplateCmd)

	// define supported flags for the get command
	getTemplateCmd.Flags().StringP(outputFlag, "o", "", "path to the output file")
	getTemplateCmd.Flags().String(actionFlag, "", "the requested action. Supported actions: ["+getSupportedActions()+"]")
	getTemplateCmd.Flags().StringP(projectFlag, "p", "", "project's name")

	// mark flags as required
	getTemplateCmd.MarkFlagRequired(actionFlag)
	getTemplateCmd.MarkFlagRequired(projectFlag)

	getCmd.AddCommand(getRecognizerCmd)

	// define supported flags for the get command
	getRecognizerCmd.Flags().StringP(outputFlag, "o", "", "path to the output file")
}
