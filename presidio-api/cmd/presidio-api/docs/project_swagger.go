package docs

import types "github.com/Microsoft/presidio-genproto/golang"

// swagger:route POST /projects/{projectID}/analyze analyze analyze
//
// Analyze text
//
// responses:
//   200: analyzeResponse

// A response includes a list of recognized fields in the text to be anonymized.
// swagger:response analyzeResponse
type analyzeResponseWrapper struct {
	// in:body
	Body []types.AnalyzeResult
}

// swagger:parameters analyze
type analyzeParamsWrapper struct {
	// The request body
	// in:body
	Body types.AnalyzeRequest

	// Used to store different configurations for different projectIDs
	// in: path
	// required: true
	ProjectID int `json:"projectID"`
}


// swagger:route POST /projects/{projectID}/anonymize anonymize anonymize
//
// Anonymize text
//
// responses:
//   200: anonymizeResponse

// A response includes anonymized text.
// swagger:response anonymizeResponse
type anonymizeResponseWrapper struct {
	// in:body
	Body types.AnonymizeResponse
}

// swagger:parameters anonymize
type anonymizeParamsWrapper struct {
	// The request body
	// in:body
	Body types.AnonymizeRequest

	// Used to store different configurations for different projectIDs
	// in: path
	// required: true
	ProjectID int `json:"projectID"`
}


// swagger:route POST /projects/{projectID}/anonymize-image anonymize-image anonymizeImage
//
// Anonymize image
//
// responses:
//   200: anonymizeImageResponse

// A response includes anonymized image.
// swagger:response anonymizeImageResponse
type anonymizeImageResponseWrapper struct {
	// in:body
	Body types.AnonymizeImageResponse
}

// swagger:parameters anonymizeImage
type anonymizeImageParamsWrapper struct {
	// The request body
	// in:body
	Body types.AnonymizeImageRequest

	// Used to store different configurations for different projectIDs
	// in: path
	// required: true
	ProjectID int `json:"projectID"`
}


// swagger:route POST /projects/{projectID}/schedule-scanner-cronjob schedule-scanner-cronjob scheduleScannerCronjob
//
// Schedule scanner cron-job
//
// responses:
//   200: scheduleScannerCronjobResponse

// A response includes the scan result.
// swagger:response scheduleScannerCronjobResponse
type scheduleScannerCronjobResponseWrapper struct {
	// in:body
	Body types.ScannerCronJobResponse
}

// swagger:parameters scheduleScannerCronjob
type scheduleScannerCronjobParamsWrapper struct {
	// The request body
	// in:body
	Body types.ScannerCronJobRequest

	// Used to store different configurations for different projectIDs
	// in: path
	// required: true
	ProjectID int `json:"projectID"`
}


// swagger:route POST /projects/{projectID}/schedule-streams-job schedule-streams-job scheduleStreamsJob
//
// Schedule streams job
//
// responses:
//   200: scheduleStreamsJobResponse

// A response includes the streams result.
// swagger:response scheduleStreamsJobResponse
type scheduleStreamsJobResponseWrapper struct {
	// in:body
	Body types.StreamsJobResponse
}

// swagger:parameters scheduleStreamsJob
type scheduleStreamsJobParamsWrapper struct {
	// in:body
	Body types.StreamsJobRequest

	// Used to store different configurations for different projectIDs
	// in: path
	// required: true
	ProjectID int `json:"projectID"`
}