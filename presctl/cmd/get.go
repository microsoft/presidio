package cmd

import (
	"net/http"

	"github.com/spf13/cobra"
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
		outputFile := getFlagValue(cmd, outputFlag)
		templateName := getFlagValue(cmd, templateFlag)
		actionName := getFlagValue(cmd, actionFlag)
		projectName := getFlagValue(cmd, projectFlag)

		getTemplate(&http.Client{}, projectName, actionName, templateName, outputFile)
	},
}

func init() {
	rootCmd.AddCommand(getCmd)
	getCmd.AddCommand(getTemplateCmd)

	// define supported flags for the add command
	getTemplateCmd.Flags().String(templateFlag, "", "template's name")
	getTemplateCmd.Flags().StringP(outputFlag, "o", "", "path to the output file")
	getTemplateCmd.Flags().String(actionFlag, "", "the requested action. Supported actions: ['anonymize', 'analyze']")
	getTemplateCmd.Flags().String(projectFlag, "", "project's name")

	// mark flags as required
	getTemplateCmd.MarkFlagRequired(templateFlag)
	getTemplateCmd.MarkFlagRequired(outputFlag)
	getTemplateCmd.MarkFlagRequired(actionFlag)
	getTemplateCmd.MarkFlagRequired(projectFlag)
}
