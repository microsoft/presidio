package cmd

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"

	"github.com/Microsoft/presidio/presctl/cmd/entities"

	"github.com/spf13/cobra"
)

// ScannerJobMsg defines the structure of the action post body
type ScannerJobMsg struct {
	ScannerCronJobTemplateID string
}

// StreamJobMsg defines the structure of the action post body
type StreamJobMsg struct {
	StreamsTemplateID string
}

func scheduleJob(cmd *cobra.Command, jobType string) {
	filePath := getFlagValue(cmd, fileFlag)
	projectName := getFlagValue(cmd, projectFlag)
	jobTemplateID := getFlagValue(cmd, scheduleJobTemplateIDFlag)

	// currently there is no way to define a 'group' if required params in cobra
	if filePath == "" && jobTemplateID == "" {
		fmt.Printf("must supply the '%s' flag or the '%s' flag", fileFlag, scheduleJobTemplateIDFlag)
		os.Exit(1)
	}

	// either create a json body from the given params, or send a given json file
	var contentStr string
	var err error
	var jsonBytes []byte
	if filePath == "" {
		if jobType == entities.Scanner {
			msg := ScannerJobMsg{ScannerCronJobTemplateID: jobTemplateID}
			jsonBytes, err = json.Marshal(&msg)
			contentStr = string(jsonBytes)
		} else {
			msg := StreamJobMsg{StreamsTemplateID: jobTemplateID}
			jsonBytes, err = json.Marshal(&msg)
			contentStr = string(jsonBytes)
		}
	} else {
		contentStr, err = getJSONFileContent(filePath)
	}
	check(err)

	// Send a REST command to presidio instance to schedule the job
	entities.ScheduleJob(&http.Client{}, jobType, projectName, contentStr)
}

var scheduleCmd = &cobra.Command{
	Use:   "schedule",
	Short: "schedule a new cron job",
}

// jobCmd represents the schedule job command
var jobCmd = &cobra.Command{
	Use:   "job",
	Short: "schedule a new cron job",
	Long:  `Use this command to schedule a new cron job.`,
}

// scannerCmd represents the schedule scanner job command
var scannerCmd = &cobra.Command{
	Use:   "scanner",
	Short: "schedule a new scanner cron job",
	Long:  `Use this command to schedule a new scanner cron job.`,
	Run: func(cmd *cobra.Command, args []string) {
		scheduleJob(cmd, entities.Scanner)
	},
}

// scannerCmd represents the schedule scanner job command
var streamCmd = &cobra.Command{
	Use:   "stream",
	Short: "schedule a new stream cron job",
	Long:  `Use this command to schedule a new stream cron job.`,
	Run: func(cmd *cobra.Command, args []string) {
		scheduleJob(cmd, entities.Stream)
	},
}

func init() {
	rootCmd.AddCommand(scheduleCmd)
	scheduleCmd.AddCommand(jobCmd)
	jobCmd.AddCommand(scannerCmd)
	jobCmd.AddCommand(streamCmd)

	// define supported flags
	scannerCmd.Flags().StringP(fileFlag, "f", "", "path to a job definition json file")
	scannerCmd.Flags().StringP(projectFlag, "p", "", "project's name")

	streamCmd.Flags().StringP(fileFlag, "f", "", "path to a job definition json file")
	streamCmd.Flags().StringP(projectFlag, "p", "", "project's name")

	scannerCmd.Flags().String(scheduleJobTemplateIDFlag, "", "the templateId")
	streamCmd.Flags().String(scheduleJobTemplateIDFlag, "", "the templateId")

	// mark flags as required
	scannerCmd.MarkFlagRequired(projectFlag)
	streamCmd.MarkFlagRequired(projectFlag)

}
