package cmd

import (
	"fmt"
	"log"
	"net/http"
	"os"

	homedir "github.com/mitchellh/go-homedir"
	"github.com/spf13/cobra"
	"github.com/spf13/viper"
)

type httpClient interface {
	Do(req *http.Request) (*http.Response, error)
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
