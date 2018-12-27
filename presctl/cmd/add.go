package cmd

import (
	"fmt"
	"net/http"
	"os"

	"github.com/spf13/cobra"
)

// constants
const fileFlag = "file"
const templateFlag = "template"
const actionFlag = "action"
const projectFlag = "project"
const outputFlag = "output"

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
		path := getFlagValue(cmd, fileFlag)
		templateName := getFlagValue(cmd, templateFlag)
		actionName := getFlagValue(cmd, actionFlag)
		projectName := getFlagValue(cmd, projectFlag)

		fileContentStr, err := getJSONFileContent(path)
		if err != nil {
			fmt.Println(err)
			os.Exit(1)
		}

		// Send a REST command to presidio instance to create the requested template
		createTemplate(&http.Client{}, projectName, actionName, templateName, fileContentStr)
	},
}

func init() {
	rootCmd.AddCommand(addCmd)
	addCmd.AddCommand(templateCmd)

	// define supported flags for the add command
	templateCmd.Flags().StringP(fileFlag, "f", "", "path to a template json file")
	templateCmd.Flags().String(templateFlag, "", "new template's name")
	templateCmd.Flags().String(actionFlag, "", "the requested action. Supported actions: ['anonymize', 'analyze']")
	templateCmd.Flags().String(projectFlag, "", "project's name")
	// mark flags as required
	templateCmd.MarkFlagRequired(fileFlag)
	templateCmd.MarkFlagRequired(templateFlag)
	templateCmd.MarkFlagRequired(actionFlag)
	templateCmd.MarkFlagRequired(projectFlag)
}
