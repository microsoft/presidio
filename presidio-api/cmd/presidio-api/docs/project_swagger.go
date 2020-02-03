package docs

import types "github.com/Microsoft/presidio-genproto/golang"

// swagger:route POST /projects/{projectID}/analyze analyze analyzeRequest
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

// swagger:parameters analyzeRequest
type analyzeParamsWrapper struct {
	// The request body
	// in:body
	Body types.AnalyzeRequest

	// in: path
	// required: true
	ProjectID int `json:"projectID"`
}


// swagger:route POST /projects/{projectID}/anonymize anonymize anonymizeRequest
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

// swagger:parameters anonymizeRequest
type anonymizeParamsWrapper struct {
	// The request body
	// in:body
	Body types.AnonymizeRequest

	// in: path
	// required: true
	ProjectID int `json:"projectID"`
}


// swagger:route POST /projects/{projectID}/anonymize-image anonymize-image anonymizeImageRequest
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

// swagger:parameters anonymizeImageRequest
type anonymizeImageParamsWrapper struct {
	// The request body
	// in:body
	Body types.AnonymizeImageRequest

	// in: path
	// required: true
	ProjectID int `json:"projectID"`
}


// swagger:route POST /projects/{projectID}/schedule-scanner-cronjob schedule-scanner-cronjob scheduleScannerCronjobRequest
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

// swagger:parameters scheduleScannerCronjobRequest
type scheduleScannerCronjobParamsWrapper struct {
	// The request body
	// in:body
	Body types.ScannerCronJobRequest

	// in: path
	// required: true
	ProjectID int `json:"projectID"`
}


// swagger:route POST /projects/{projectID}/schedule-streams-job schedule-streams-job scheduleStreamsJobRequest
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

// swagger:parameters scheduleStreamsJobRequest
type scheduleStreamsJobParamsWrapper struct {
	// in:body
	Body types.StreamsJobRequest

	// in: path
	// required: true
	ProjectID int `json:"projectID"`
}