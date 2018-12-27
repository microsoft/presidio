package cmd

import (
	"fmt"
	"net/http"

	"github.com/spf13/cobra"
)

// updateCmd represents the update command
var updateCmd = &cobra.Command{
	Use:   "update",
	Short: "update a specific resource type",
	Long:  `Use this command to update a resource of the specified type.`,
}

var updateTemplateCmd = &cobra.Command{
	Use:   "template",
	Short: "update a template resource",
	Long:  `Use this command to update presidio template.`,
	Run: func(cmd *cobra.Command, args []string) {
		path := getFlagValue(cmd, fileFlag)
		templateName := getFlagValue(cmd, templateFlag)
		actionName := getFlagValue(cmd, actionFlag)
		projectName := getFlagValue(cmd, projectFlag)

		fileContentStr, err := getJSONFileContent(path)
		if err != nil {
			fmt.Println(err)
			return
		}

		updateTemplate(&http.Client{}, projectName, actionName, templateName, fileContentStr)
	},
}

func init() {
	rootCmd.AddCommand(updateCmd)
	updateCmd.AddCommand(updateTemplateCmd)

	// define supported flags for the add command
	updateTemplateCmd.Flags().StringP(fileFlag, "f", "", "path to a template json file")
	updateTemplateCmd.Flags().String(templateFlag, "", "template's name")
	updateTemplateCmd.Flags().String(actionFlag, "", "the requested action. Supported actions: ['anonymize', 'analyze']")
	updateTemplateCmd.Flags().String(projectFlag, "", "project's name")

	// mark flags as required
	templateCmd.MarkFlagRequired(fileFlag)
	updateTemplateCmd.MarkFlagRequired(templateFlag)
	updateTemplateCmd.MarkFlagRequired(actionFlag)
	updateTemplateCmd.MarkFlagRequired(projectFlag)
}
