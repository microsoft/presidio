package cmd

import (
	"net/http"

	"github.com/Microsoft/presidio/presctl/cmd/entities"

	"github.com/spf13/cobra"
)

// addCmd represents the add command
var addCmd = &cobra.Command{
	Use:   "add",
	Short: "adds a new resource type",
	Long:  `Use this command to add to Presidio a new resource of the specified type.`,
}

// templateCmd represents the template command
var templateCmd = &cobra.Command{
	Use:   "template [name]",
	Args:  cobra.MinimumNArgs(1),
	Short: "adds a new template resource",
	Long:  `Use this command to add to presidio a new template.`,
	Run: func(cmd *cobra.Command, args []string) {
		actionName := getFlagValue(cmd, actionFlag)
		path := getFlagValue(cmd, fileFlag)
		templateString := getFlagValue(cmd, templateFlag)
		projectName := getFlagValue(cmd, projectFlag)
		templateName := args[0]

		// Get the template content either by reading a file or inline, exit if encounter an error
		contentStr := getContentString(path, templateString, "Template")

		// Send a REST command to presidio instance to create the requested template
		entities.CreateTemplate(&http.Client{}, projectName, actionName, templateName, contentStr)
	},
}

// recognizerCmd represents a custom analysis recognizer
var recognizerCmd = &cobra.Command{
	Use:   "recognizer [name]",
	Args:  cobra.MinimumNArgs(1),
	Short: "adds a new custom recognizer resource",
	Long:  `Use this command to add to Presidio a new custom recognizer.`,
	Run: func(cmd *cobra.Command, args []string) {
		path := getFlagValue(cmd, fileFlag)
		recognizerName := args[0]
		recognizerString := getFlagValue(cmd, recognizerFlag)

		// Get the recognizer content either by reading a file or inline, exit if encounter an error
		contentStr := getContentString(path, recognizerString, "Recognizer")

		// Send a REST command to presidio instance to create the requested template
		entities.CreateRecognizer(&http.Client{}, recognizerName, contentStr)
	},
}

func init() {
	rootCmd.AddCommand(addCmd)
	addCmd.AddCommand(templateCmd)

	// define supported flags for the add command
	templateCmd.Flags().StringP(fileFlag, "f", "", "path to a template json file")
	templateCmd.Flags().String(actionFlag, "", "the requested action. Supported actions: ["+getSupportedActions()+"]")
	templateCmd.Flags().StringP(projectFlag, "p", "", "project's name")
	templateCmd.Flags().StringP(templateFlag, "s", "", "inline template content")

	// mark flags as required
	templateCmd.MarkFlagRequired(actionFlag)
	templateCmd.MarkFlagRequired(projectFlag)

	addCmd.AddCommand(recognizerCmd)

	// define supported flags for the add command
	recognizerCmd.Flags().StringP(fileFlag, "f", "", "path to a recognizer json file")
	recognizerCmd.Flags().StringP(recognizerFlag, "s", "", "inline recognizer content")
}
