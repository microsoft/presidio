package cmd

import (
	"net/http"

	"github.com/spf13/cobra"
)

// deleteCmd represents the delete command
var deleteCmd = &cobra.Command{
	Use:   "delete",
	Short: "delete a specific resource type",
	Long:  `Use this command to delete a resource of the specified type.`,
}

var delTemplateCmd = &cobra.Command{
	Use:   "template",
	Short: "delete a template resource",
	Long:  `Use this command to delete a template from presidio.`,
	Run: func(cmd *cobra.Command, args []string) {
		actionName := getFlagValue(cmd, actionFlag)
		projectName := getFlagValue(cmd, projectFlag)
		templateName := getFlagValue(cmd, templateFlag)

		// Send a REST command to presidio instance to delete the requested template
		deleteTemplate(&http.Client{}, projectName, actionName, templateName)
	},
}

func init() {
	rootCmd.AddCommand(deleteCmd)
	deleteCmd.AddCommand(delTemplateCmd)

	// define supported flags for the add command
	delTemplateCmd.Flags().String(templateFlag, "", "template's name")
	delTemplateCmd.Flags().String(actionFlag, "", "the requested action. Supported actions: ['anonymize', 'analyze']")
	delTemplateCmd.Flags().String(projectFlag, "", "project's name")

	// mark flags as required
	delTemplateCmd.MarkFlagRequired(templateFlag)
	delTemplateCmd.MarkFlagRequired(actionFlag)
	delTemplateCmd.MarkFlagRequired(projectFlag)
}
