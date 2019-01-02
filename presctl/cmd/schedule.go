package cmd

import (
	"net/http"

	"github.com/Microsoft/presidio/presctl/cmd/entities"

	"github.com/spf13/cobra"
)

func scheduleJob(cmd *cobra.Command, jobType string) {
	filePath := getFlagValue(cmd, fileFlag)
	projectName := getFlagValue(cmd, projectFlag)

	fileContentStr, err := getJSONFileContent(filePath)
	check(err)

	// Send a REST command to presidio instance to schedule the job
	entities.ScheduleJob(&http.Client{}, jobType, projectName, fileContentStr)
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
	scannerCmd.Flags().String(projectFlag, "", "project's name")

	streamCmd.Flags().StringP(fileFlag, "f", "", "path to a job definition json file")
	streamCmd.Flags().String(projectFlag, "", "project's name")

	// mark flags as required
	scannerCmd.MarkFlagRequired(fileFlag)
	scannerCmd.MarkFlagRequired(projectFlag)

	streamCmd.MarkFlagRequired(fileFlag)
	streamCmd.MarkFlagRequired(projectFlag)

}
