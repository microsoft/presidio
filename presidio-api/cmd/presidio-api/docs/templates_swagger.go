package docs

import types "github.com/Microsoft/presidio-genproto/golang"

// swagger:route POST /templates/{projectId}/analyze/{templateId} template analyze postAnalyzeTemplateRequest
//
// Create analyze template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route PUT /templates/{projectId}/analyze/{templateId} template analyze putAnalyzeTemplateRequest
//
// Update analyze template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route GET /templates/{projectId}/analyze/{templateId} template analyze getAnalyzeTemplateRequest
//
// Get analyze template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route DELETE /templates/{projectId}/analyze/{templateId} template analyze deleteAnalyzeTemplateRequest
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

	// in: path
	// required: true
	ProjectId string `json:"projectId"`

	// in: path
	// required: true
	TemplateId string `json:"templateId"`
}




// swagger:route POST /templates/{projectId}/anonymize/{templateId} template anonymize postAnonymizeTemplateRequest
//
// Create anonymize template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route PUT /templates/{projectId}/anonymize/{templateId} template anonymize putAnonymizeTemplateRequest
//
// Update anonymize template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route GET /templates/{projectId}/anonymize/{templateId} template anonymize getAnonymizeTemplateRequest
//
// Get anonymize template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route DELETE /templates/{projectId}/anonymize/{templateId} template anonymize deleteAnonymizeTemplateRequest
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

	// in: path
	// required: true
	ProjectId string `json:"projectId"`

	// in: path
	// required: true
	TemplateId string `json:"templateId"`
}




// swagger:route POST /templates/{projectId}/anonymize-image/{templateId} template anonymize-image postAnonymizeImageTemplateRequest
//
// Create anonymize-image template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route PUT /templates/{projectId}/anonymize-image/{templateId} template anonymize-image putAnonymizeImageTemplateRequest
//
// Update anonymize-image template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route GET /templates/{projectId}/anonymize-image/{templateId} template anonymize-image getAnonymizeImageTemplateRequest
//
// Get anonymize-image template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route DELETE /templates/{projectId}/anonymize-image/{templateId} template anonymize-image deleteAnonymizeImageTemplateRequest
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

	// in: path
	// required: true
	ProjectId string `json:"projectId"`

	// in: path
	// required: true
	TemplateId string `json:"templateId"`
}




// swagger:route POST /templates/{projectId}/scan/{templateId} template scan postScanTemplateRequest
//
// Create scan template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route PUT /templates/{projectId}/scan/{templateId} template scan putScanTemplateRequest
//
// Update scan template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route GET /templates/{projectId}/scan/{templateId} template scan getScanTemplateRequest
//
// Get scan template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route DELETE /templates/{projectId}/scan/{templateId} template scan deleteScanTemplateRequest
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

	// in: path
	// required: true
	ProjectId string `json:"projectId"`

	// in: path
	// required: true
	TemplateId string `json:"templateId"`
}




// swagger:route POST /templates/{projectId}/stream/{templateId} template stream postStreamTemplateRequest
//
// Create stream template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route PUT /templates/{projectId}/stream/{templateId} template stream putStreamTemplateRequest
//
// Update stream template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route GET /templates/{projectId}/stream/{templateId} template stream getStreamTemplateRequest
//
// Get stream template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route DELETE /templates/{projectId}/stream/{templateId} template stream deleteStreamTemplateRequest
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

	// in: path
	// required: true
	ProjectId string `json:"projectId"`

	// in: path
	// required: true
	TemplateId string `json:"templateId"`
}




// swagger:route POST /templates/{projectId}/datasink/{templateId} template datasink postDatasinkTemplateRequest
//
// Create datasink template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route PUT /templates/{projectId}/datasink/{templateId} template datasink putDatasinkTemplateRequest
//
// Update datasink template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route GET /templates/{projectId}/datasink/{templateId} template datasink getDatasinkTemplateRequest
//
// Get datasink template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route DELETE /templates/{projectId}/datasink/{templateId} template datasink deleteDatasinkTemplateRequest
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

	// in: path
	// required: true
	ProjectId string `json:"projectId"`

	// in: path
	// required: true
	TemplateId string `json:"templateId"`
}





// swagger:route POST /templates/{projectId}/schedule-scanner-cronjob/{templateId} template schedule-scanner-cronjob postScannerCronJobTemplateRequest
//
// Create schedule-scanner-cronjob template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route PUT /templates/{projectId}/schedule-scanner-cronjob/{templateId} template schedule-scanner-cronjob putScannerCronJobTemplateRequest
//
// Update schedule-scanner-cronjob template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route GET /templates/{projectId}/schedule-scanner-cronjob/{templateId} template schedule-scanner-cronjob getScannerCronJobTemplateRequest
//
// Get schedule-scanner-cronjob template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route DELETE /templates/{projectId}/schedule-scanner-cronjob/{templateId} template schedule-scanner-cronjob deleteScannerCronJobTemplateRequest
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

	// in: path
	// required: true
	ProjectId string `json:"projectId"`

	// in: path
	// required: true
	TemplateId string `json:"templateId"`
}




// swagger:route POST /templates/{projectId}/schedule-streams-job/{templateId} template schedule-streams-job postStreamsJobTemplateRequest
//
// Create schedule-streams-job template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route PUT /templates/{projectId}/schedule-streams-job/{templateId} template schedule-streams-job putStreamsJobTemplateRequest
//
// Update schedule-streams-job template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route GET /templates/{projectId}/schedule-streams-job/{templateId} template schedule-streams-job getStreamsJobTemplateRequest
//
// Get schedule-streams-job template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route DELETE /templates/{projectId}/schedule-streams-job/{templateId} template schedule-streams-job deleteStreamsJobTemplateRequest
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

	// in: path
	// required: true
	ProjectId string `json:"projectId"`

	// in: path
	// required: true
	TemplateId string `json:"templateId"`
}


// swagger:parameters getStreamsJobTemplateRequest deleteStreamsJobTemplateRequest getScannerCronJobTemplateRequest deleteScannerCronJobTemplateRequest getDatasinkTemplateRequest deleteDatasinkTemplateRequest getStreamTemplateRequest deleteStreamTemplateRequest getScanTemplateRequest deleteScanTemplateRequest getAnonymizeImageTemplateRequest deleteAnonymizeImageTemplateRequest getAnonymizeTemplateRequest deleteAnonymizeTemplateRequest getAnalyzeTemplateRequest deleteAnalyzeTemplateRequest
type templateGeneralParamsWrapper struct {
	// in: path
	// required: true
	ProjectId string `json:"projectId"`

	// in: path
	// required: true
	TemplateId string `json:"templateId"`
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

