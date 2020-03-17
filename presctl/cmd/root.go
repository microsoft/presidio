package cmd

import (
	"encoding/json"
	"errors"
	"fmt"
	"io/ioutil"
	"os"
	"strings"

	homedir "github.com/mitchellh/go-homedir"
	"github.com/spf13/cobra"
	"github.com/spf13/viper"
)

const (
	analyze                = "analyze"
	anonymize              = "anonymize"
	scan                   = "scan"
	stream                 = "stream"
	datasink               = "datasink"
	scheduleScannerCronJob = "schedule-scanner-cronjob"
	scheduleStreamsJob     = "schedule-streams-job"
)

// allowedActions all of the allowed action that Presidio is offering
var allowedActions = []string{analyze, anonymize, scan, stream, datasink, scheduleScannerCronJob, scheduleStreamsJob}

// constants
const (
	fileFlag                  = "file"
	actionFlag                = "action"
	stringFlag                = "string"
	projectFlag               = "project"
	outputFlag                = "output"
	analyzeTemplateIDFlag     = "analyze-template-id"
	anonymizeTemplateIDFlag   = "anonymize-template-id"
	scheduleJobTemplateIDFlag = "jobTemplateId"
	templateFlag              = "template"
	recognizerFlag            = "recognizer"
)

func getSupportedActions() string {
	return strings.Join(allowedActions, ", ")
}

func check(err error) {
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
}

// isJson returns true if the given string is a valid JSON
func isJSON(s string) bool {
	var js map[string]interface{}
	return json.Unmarshal([]byte(s), &js) == nil
}

// getJSONFileContent reads the content of a given file and if the content is a
// valid JSON returns it
func getJSONFileContent(path string) (string, error) {
	fileContentBytes, err := ioutil.ReadFile(path)
	if err != nil {
		return "", fmt.Errorf("Failed reading file %s", path)
	}

	fileContentStr := string(fileContentBytes)
	return fileContentStr, nil
}

// getContentString gets the object content from the given path or thhe inline argument.
// Exits with 1 if an illegal situation occurs (no value provided or two values were provided)
func getContentString(path string, inlineValue string, objectType string) string {
	var contentStr string
	var err error

	if path == "" && inlineValue == "" {
		err = errors.New(objectType + " file or " + strings.ToLower(objectType) + " content must be provided")
	} else if path != "" && inlineValue != "" {
		err = errors.New("Can't supply both " + strings.ToLower(objectType) + " file and inline " + strings.ToLower(objectType) + " content")
	} else if inlineValue == "" {
		contentStr, err = getJSONFileContent(path)
	} else {
		contentStr = inlineValue
	}
	check(err)

	isValidJSON := isJSON(contentStr)

	if !isValidJSON {
		err = errors.New("The given " + strings.ToLower(objectType) + " file is not a valid json")
	}
	check(err)

	return contentStr
}

func getFlagValue(cmd *cobra.Command, flagName string) string {
	result, err := cmd.Flags().GetString(flagName)
	if err != nil {
		fmt.Printf("Failed getting '%s' flag", flagName)
		os.Exit(1)
	}

	return result
}

var cfgFile string

// rootCmd represents the base command when called without any subcommands
var rootCmd = &cobra.Command{
	Use:   "presctl",
	Short: "presctl controls the Presidio instance",
	Long: `The presctl controls the Presidio instance
It exposes Presidio's API as well as provides a simple way to control the Presidio kubernetes deployment.`,
}

// Execute adds all child commands to the root command and sets flags appropriately.
// This is called by main.main(). It only needs to happen once to the rootCmd.
func Execute() {
	if err := rootCmd.Execute(); err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
}

func init() {
	cobra.OnInitialize(initConfig)

	rootCmd.PersistentFlags().StringVar(&cfgFile, "config", "", "config file (default is $HOME/.presctl.yaml)")
	rootCmd.Flags().BoolP("toggle", "t", false, "Help message for toggle")
}

// initConfig reads in config file and ENV variables if set.
func initConfig() {
	if cfgFile != "" {
		// Use config file from the flag.
		viper.SetConfigFile(cfgFile)
	} else {
		// Find home directory.
		home, err := homedir.Dir()
		if err != nil {
			fmt.Println(err)
			os.Exit(1)
		}

		// Search config in home directory with name ".presctl" (without extension).
		viper.AddConfigPath(home)
		viper.SetConfigName(".presctl")
	}

	viper.AutomaticEnv() // read in environment variables that match

	// If a config file is found, read it in.
	if err := viper.ReadInConfig(); err == nil {
		fmt.Println("Using config file:", viper.ConfigFileUsed())
	}
}
