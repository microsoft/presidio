package cmd

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"strings"

	homedir "github.com/mitchellh/go-homedir"
	"github.com/spf13/cobra"
	"github.com/spf13/viper"

	"github.com/Microsoft/presidio/pkg/presidio"
)

// constants
const (
	fileFlag                  = "file"
	templateFlag              = "template"
	actionFlag                = "action"
	stringFlag                = "string"
	projectFlag               = "project"
	outputFlag                = "output"
	analyzeTemplateIDFlag     = "analyzeTemplateId"
	anonymizeTemplateIDFlag   = "anonymizeTemplateId"
	scheduleJobTemplateIDFlag = "jobTemplateId"
)

func getSupportedActions() string {
	return strings.Join(presidio.AllowedActions, ", ")
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
	isValidJSON := isJSON(fileContentStr)

	if !isValidJSON {
		errMsg := "The given template file is not a valid json file or does not exists"
		fmt.Println(errMsg)
		return "", fmt.Errorf(errMsg)
	}
	return fileContentStr, nil
}

func getFlagValue(cmd *cobra.Command, flagName string) string {
	result, err := cmd.Flags().GetString(flagName)
	if err != nil {
		log.Printf("Failed getting '%s' flag", flagName)
		panic(err)
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
