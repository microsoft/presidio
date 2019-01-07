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
	Long:  `Use this command to add to presidio a new resource of the specified type.`,
}

// templateCmd represents the template command
var templateCmd = &cobra.Command{
	Use:   "template",
	Short: "adds a new template resource",
	Long:  `Use this command to add to presidio a new template.`,
	Run: func(cmd *cobra.Command, args []string) {
		actionName := getFlagValue(cmd, actionFlag)
		path := getFlagValue(cmd, fileFlag)
		projectName := getFlagValue(cmd, projectFlag)
		templateName := getFlagValue(cmd, templateFlag)

		fileContentStr, err := getJSONFileContent(path)
		check(err)

		// Send a REST command to presidio instance to create the requested template
		entities.CreateTemplate(&http.Client{}, projectName, actionName, templateName, fileContentStr)
	},
}

func init() {
	rootCmd.AddCommand(addCmd)
	addCmd.AddCommand(templateCmd)

	// define supported flags for the add command
	templateCmd.Flags().StringP(fileFlag, "f", "", "path to a template json file")
	templateCmd.Flags().String(templateFlag, "", "new template's name")
	templateCmd.Flags().String(actionFlag, "", "the requested action. Supported actions: ["+getSupportedActions()+"]")
	templateCmd.Flags().String(projectFlag, "", "project's name")

	// mark flags as required
	templateCmd.MarkFlagRequired(fileFlag)
	templateCmd.MarkFlagRequired(templateFlag)
	templateCmd.MarkFlagRequired(actionFlag)
	templateCmd.MarkFlagRequired(projectFlag)
}
