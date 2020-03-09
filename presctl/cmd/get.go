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
	Short: "adds a new template resource",
	Long:  `Use this command to add to presidio a new template.`,
	Run: func(cmd *cobra.Command, args []string) {
		actionName := getFlagValue(cmd, actionFlag)
		outputFile := getFlagValue(cmd, outputFlag)
		projectName := getFlagValue(cmd, projectFlag)
		templateName := getFlagValue(cmd, templateFlag)

		// Send a REST command to presidio instance to get the requested template
		entities.GetTemplate(&http.Client{}, projectName, actionName, templateName, outputFile)
	},
}

func init() {
	rootCmd.AddCommand(getCmd)
	getCmd.AddCommand(getTemplateCmd)

	// define supported flags for the add command
	getTemplateCmd.Flags().String(templateFlag, "", "template's name")
	getTemplateCmd.Flags().StringP(outputFlag, "o", "", "path to the output file")
	getTemplateCmd.Flags().String(actionFlag, "", "the requested action. Supported actions: ["+getSupportedActions()+"]")
	getTemplateCmd.Flags().String(projectFlag, "", "project's name")

	// mark flags as required
	getTemplateCmd.MarkFlagRequired(templateFlag)
	getTemplateCmd.MarkFlagRequired(actionFlag)
	getTemplateCmd.MarkFlagRequired(projectFlag)
}
