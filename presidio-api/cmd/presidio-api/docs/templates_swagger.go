package docs

import types "github.com/Microsoft/presidio-genproto/golang"

// swagger:route POST /templates/{projectID}/analyze/{templateID} template analyze postAnalyzeTemplateRequest
//
// Create analyze template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route PUT /templates/{projectID}/analyze/{templateID} template analyze putAnalyzeTemplateRequest
//
// Update analyze template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route GET /templates/{projectID}/analyze/{templateID} template analyze getAnalyzeTemplateRequest
//
// Get analyze template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route DELETE /templates/{projectID}/analyze/{templateID} template analyze deleteAnalyzeTemplateRequest
//
// Delete analyze template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:parameters postAnalyzeTemplateRequest putAnalyzeTemplateRequest
type postAnalyzeTemplateParamsWrapper struct {
	// The request body
	// in:body
	Body types.AnalyzeTemplate

	// Used to store different configurations for different projectIDs
	// in: path
	// required: true
	ProjectID string `json:"projectID"`

	// in: path
	// required: true
	TemplateID string `json:"templateID"`
}




// swagger:route POST /templates/{projectID}/anonymize/{templateID} template anonymize postAnonymizeTemplateRequest
//
// Create anonymize template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route PUT /templates/{projectID}/anonymize/{templateID} template anonymize putAnonymizeTemplateRequest
//
// Update anonymize template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route GET /templates/{projectID}/anonymize/{templateID} template anonymize getAnonymizeTemplateRequest
//
// Get anonymize template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route DELETE /templates/{projectID}/anonymize/{templateID} template anonymize deleteAnonymizeTemplateRequest
//
// Delete anonymize template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:parameters postAnonymizeTemplateRequest putAnonymizeTemplateRequest
type postAnonymizeTemplateParamsWrapper struct {
	// The request body
	// in:body
	Body types.AnonymizeTemplate

	// Used to store different configurations for different projectIDs
	// in: path
	// required: true
	ProjectID string `json:"projectID"`

	// in: path
	// required: true
	TemplateID string `json:"templateID"`
}




// swagger:route POST /templates/{projectID}/anonymize-image/{templateID} template anonymize-image postAnonymizeImageTemplateRequest
//
// Create anonymize-image template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route PUT /templates/{projectID}/anonymize-image/{templateID} template anonymize-image putAnonymizeImageTemplateRequest
//
// Update anonymize-image template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route GET /templates/{projectID}/anonymize-image/{templateID} template anonymize-image getAnonymizeImageTemplateRequest
//
// Get anonymize-image template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route DELETE /templates/{projectID}/anonymize-image/{templateID} template anonymize-image deleteAnonymizeImageTemplateRequest
//
// Delete anonymize-image template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError

// swagger:parameters postAnonymizeImageTemplateRequest putAnonymizeImageTemplateRequest
type postAnonymizeImageTemplateParamsWrapper struct {
	// The request body
	// in:body
	Body types.AnonymizeImageTemplate

	// Used to store different configurations for different projectIDs
	// in: path
	// required: true
	ProjectID string `json:"projectID"`

	// in: path
	// required: true
	TemplateID string `json:"templateID"`
}




// swagger:route POST /templates/{projectID}/scan/{templateID} template scan postScanTemplateRequest
//
// Create scan template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route PUT /templates/{projectID}/scan/{templateID} template scan putScanTemplateRequest
//
// Update scan template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route GET /templates/{projectID}/scan/{templateID} template scan getScanTemplateRequest
//
// Get scan template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route DELETE /templates/{projectID}/scan/{templateID} template scan deleteScanTemplateRequest
//
// Delete scan template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:parameters postScanTemplateRequest putScanTemplateRequest
type postScanTemplateParamsWrapper struct {
	// The request body
	// in:body
	Body types.ScanTemplate

	// Used to store different configurations for different projectIDs
	// in: path
	// required: true
	ProjectID string `json:"projectID"`

	// in: path
	// required: true
	TemplateID string `json:"templateID"`
}




// swagger:route POST /templates/{projectID}/stream/{templateID} template stream postStreamTemplateRequest
//
// Create stream template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route PUT /templates/{projectID}/stream/{templateID} template stream putStreamTemplateRequest
//
// Update stream template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route GET /templates/{projectID}/stream/{templateID} template stream getStreamTemplateRequest
//
// Get stream template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route DELETE /templates/{projectID}/stream/{templateID} template stream deleteStreamTemplateRequest
//
// Delete stream template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:parameters postStreamTemplateRequest putStreamTemplateRequest
type postStreamTemplateParamsWrapper struct {
	// The request body
	// in:body
	Body types.StreamTemplate

	// Used to store different configurations for different projectIDs
	// in: path
	// required: true
	ProjectID string `json:"projectID"`

	// in: path
	// required: true
	TemplateID string `json:"templateID"`
}




// swagger:route POST /templates/{projectID}/datasink/{templateID} template datasink postDatasinkTemplateRequest
//
// Create datasink template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route PUT /templates/{projectID}/datasink/{templateID} template datasink putDatasinkTemplateRequest
//
// Update datasink template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route GET /templates/{projectID}/datasink/{templateID} template datasink getDatasinkTemplateRequest
//
// Get datasink template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route DELETE /templates/{projectID}/datasink/{templateID} template datasink deleteDatasinkTemplateRequest
//
// Delete datasink template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:parameters postDatasinkTemplateRequest putDatasinkTemplateRequest
type postDatasinkTemplateParamsWrapper struct {
	// The request body
	// in:body
	Body types.DatasinkTemplate

	// Used to store different configurations for different projectIDs
	// in: path
	// required: true
	ProjectID string `json:"projectID"`

	// in: path
	// required: true
	TemplateID string `json:"templateID"`
}





// swagger:route POST /templates/{projectID}/schedule-scanner-cronjob/{templateID} template schedule-scanner-cronjob postScannerCronJobTemplateRequest
//
// Create schedule-scanner-cronjob template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route PUT /templates/{projectID}/schedule-scanner-cronjob/{templateID} template schedule-scanner-cronjob putScannerCronJobTemplateRequest
//
// Update schedule-scanner-cronjob template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route GET /templates/{projectID}/schedule-scanner-cronjob/{templateID} template schedule-scanner-cronjob getScannerCronJobTemplateRequest
//
// Get schedule-scanner-cronjob template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route DELETE /templates/{projectID}/schedule-scanner-cronjob/{templateID} template schedule-scanner-cronjob deleteScannerCronJobTemplateRequest
//
// Delete schedule-scanner-cronjob template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:parameters postScannerCronJobTemplateRequest putScannerCronJobTemplateRequest
type postScannerCronJobTemplateParamsWrapper struct {
	// The request body
	// in:body
	Body types.ScannerCronJobTemplate

	// Used to store different configurations for different projectIDs
	// in: path
	// required: true
	ProjectID string `json:"projectID"`

	// in: path
	// required: true
	TemplateID string `json:"templateID"`
}




// swagger:route POST /templates/{projectID}/schedule-streams-job/{templateID} template schedule-streams-job postStreamsJobTemplateRequest
//
// Create schedule-streams-job template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route PUT /templates/{projectID}/schedule-streams-job/{templateID} template schedule-streams-job putStreamsJobTemplateRequest
//
// Update schedule-streams-job template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route GET /templates/{projectID}/schedule-streams-job/{templateID} template schedule-streams-job getStreamsJobTemplateRequest
//
// Get schedule-streams-job template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route DELETE /templates/{projectID}/schedule-streams-job/{templateID} template schedule-streams-job deleteStreamsJobTemplateRequest
//
// Delete schedule-streams-job template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:parameters postStreamsJobTemplateRequest putStreamsJobTemplateRequest
type postStreamsJobTemplateParamsWrapper struct {
	// The request body
	// in:body
	Body types.StreamsJobTemplate

	// Used to store different configurations for different projectIDs
	// in: path
	// required: true
	ProjectID string `json:"projectID"`

	// in: path
	// required: true
	TemplateID string `json:"templateID"`
}


// swagger:parameters getStreamsJobTemplateRequest deleteStreamsJobTemplateRequest getScannerCronJobTemplateRequest deleteScannerCronJobTemplateRequest getDatasinkTemplateRequest deleteDatasinkTemplateRequest getStreamTemplateRequest deleteStreamTemplateRequest getScanTemplateRequest deleteScanTemplateRequest getAnonymizeImageTemplateRequest deleteAnonymizeImageTemplateRequest getAnonymizeTemplateRequest deleteAnonymizeTemplateRequest getAnalyzeTemplateRequest deleteAnalyzeTemplateRequest
type templateGeneralParamsWrapper struct {
	// Used to store different configurations for different projectIDs	// in: path
	// in: path
	// required: true
	ProjectID string `json:"projectID"`

	// in: path
	// required: true
	TemplateID string `json:"templateID"`
}


// Response message
// swagger:response templateGeneralResponse
type templateGeneralResponseWrapper struct {
	// The response message
	// in:body
	Data string `json:"data"`
}

// Response error
// swagger:response templateGeneralError
type templateGeneralErrorWrapper struct {
	// The error message
	// in:body
	Data string `json:"data"`
}

