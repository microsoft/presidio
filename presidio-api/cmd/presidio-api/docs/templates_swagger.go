package docs

import types "github.com/Microsoft/presidio-genproto/golang"

// swagger:route POST /templates/{projectId}/analyze/{templateId} template postAnalyzeTemplateRequest
//
// Create analyze template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route PUT /templates/{projectId}/analyze/{templateId} template postAnalyzeTemplateRequest
//
// Update analyze template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route GET /templates/{projectId}/analyze/{templateId} template analyzeTemplateRequest
//
// Get analyze template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route DELETE /templates/{projectId}/analyze/{templateId} template analyzeTemplateRequest
//
// Delete analyze template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:parameters postAnalyzeTemplateRequest
type postAnalyzeTemplateParamsWrapper struct {
	// The request body
	// in:body
	Body types.AnalyzeTemplate

	// in: path
	// required: true
	ProjectId int `json:"projectId"`

	// in: path
	// required: true
	TemplateId string `json:"templateId"`
}

// swagger:parameters analyzeTemplateRequest
type analyzeTemplateParamsWrapper struct {
	// in: path
	// required: true
	ProjectId int `json:"projectId"`

	// in: path
	// required: true
	TemplateId string `json:"templateId"`
}


// swagger:route POST /templates/{projectId}/anonymize/{templateId} template postAnonymizeTemplateRequest
//
// Create anonymize template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route PUT /templates/{projectId}/anonymize/{templateId} template postAnonymizeTemplateRequest
//
// Update anonymize template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route GET /templates/{projectId}/anonymize/{templateId} template postAnonymizeTemplateRequest
//
// Get anonymize template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route DELETE /templates/{projectId}/anonymize/{templateId} template postAnonymizeTemplateRequest
//
// Delete anonymize template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:parameters postAnonymizeTemplateRequest
type postAnonymizeTemplateParamsWrapper struct {
	// The request body
	// in:body
	Body types.AnonymizeTemplate

	// in: path
	// required: true
	ProjectId int `json:"projectId"`

	// in: path
	// required: true
	TemplateId string `json:"templateId"`
}

// swagger:parameters anonymizeTemplateRequest
type anonymizeTemplateParamsWrapper struct {
	// in: path
	// required: true
	ProjectId int `json:"projectId"`

	// in: path
	// required: true
	TemplateId string `json:"templateId"`
}





// swagger:route POST /templates/{projectId}/anonymize-image/{templateId} template postAnonymizeImageTemplateRequest
//
// Create anonymize-image template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route PUT /templates/{projectId}/anonymize-image/{templateId} template postAnonymizeImageTemplateRequest
//
// Update anonymize-image template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route GET /templates/{projectId}/anonymize-image/{templateId} template postAnonymizeImageTemplateRequest
//
// Get anonymize-image template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route DELETE /templates/{projectId}/anonymize-image/{templateId} template postAnonymizeImageTemplateRequest
//
// Delete anonymize-image template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError

// swagger:parameters postAnonymizeImageTemplateRequest
type postAnonymizeImageTemplateParamsWrapper struct {
	// The request body
	// in:body
	Body types.AnonymizeImageTemplate

	// in: path
	// required: true
	ProjectId int `json:"projectId"`

	// in: path
	// required: true
	TemplateId string `json:"templateId"`
}







// swagger:route POST /templates/{projectId}/scan/{templateId} template postScanTemplateRequest
//
// Create scan template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route PUT /templates/{projectId}/scan/{templateId} template postScanTemplateRequest
//
// Update scan template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route GET /templates/{projectId}/scan/{templateId} template postScanTemplateRequest
//
// Get scan template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route DELETE /templates/{projectId}/scan/{templateId} template postScanTemplateRequest
//
// Delete scan template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:parameters postScanTemplateRequest
type postScanTemplateParamsWrapper struct {
	// The request body
	// in:body
	Body types.ScanTemplate

	// in: path
	// required: true
	ProjectId int `json:"projectId"`

	// in: path
	// required: true
	TemplateId string `json:"templateId"`
}







// swagger:route POST /templates/{projectId}/stream/{templateId} template postStreamTemplateRequest
//
// Create stream template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route PUT /templates/{projectId}/stream/{templateId} template postStreamTemplateRequest
//
// Update stream template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route GET /templates/{projectId}/stream/{templateId} template postStreamTemplateRequest
//
// Get stream template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route DELETE /templates/{projectId}/stream/{templateId} template postStreamTemplateRequest
//
// Delete stream template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:parameters postStreamTemplateRequest
type postStreamTemplateParamsWrapper struct {
	// The request body
	// in:body
	Body types.StreamTemplate

	// in: path
	// required: true
	ProjectId int `json:"projectId"`

	// in: path
	// required: true
	TemplateId string `json:"templateId"`
}








// swagger:route POST /templates/{projectId}/datasink/{templateId} template postDatasinkTemplateRequest
//
// Create datasink template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route PUT /templates/{projectId}/datasink/{templateId} template postDatasinkTemplateRequest
//
// Update datasink template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route GET /templates/{projectId}/datasink/{templateId} template postDatasinkTemplateRequest
//
// Get datasink template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route DELETE /templates/{projectId}/datasink/{templateId} template postDatasinkTemplateRequest
//
// Delete datasink template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:parameters postDatasinkTemplateRequest
type postDatasinkTemplateParamsWrapper struct {
	// The request body
	// in:body
	Body types.DatasinkTemplate

	// in: path
	// required: true
	ProjectId int `json:"projectId"`

	// in: path
	// required: true
	TemplateId string `json:"templateId"`
}








// swagger:route POST /templates/{projectId}/schedule-scanner-cronjob/{templateId} template postScannerCronJobTemplateRequest
//
// Create schedule-scanner-cronjob template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route PUT /templates/{projectId}/schedule-scanner-cronjob/{templateId} template postScannerCronJobTemplateRequest
//
// Update schedule-scanner-cronjob template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route GET /templates/{projectId}/schedule-scanner-cronjob/{templateId} template postScannerCronJobTemplateRequest
//
// Get schedule-scanner-cronjob template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route DELETE /templates/{projectId}/schedule-scanner-cronjob/{templateId} template postScannerCronJobTemplateRequest
//
// Delete schedule-scanner-cronjob template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:parameters postScannerCronJobTemplateRequest
type postScannerCronJobTemplateParamsWrapper struct {
	// The request body
	// in:body
	Body types.ScannerCronJobTemplate

	// in: path
	// required: true
	ProjectId int `json:"projectId"`

	// in: path
	// required: true
	TemplateId string `json:"templateId"`
}







// swagger:route POST /templates/{projectId}/schedule-streams-job/{templateId} template postStreamsJobTemplateRequest
//
// Create schedule-streams-job template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route PUT /templates/{projectId}/schedule-streams-job/{templateId} template postStreamsJobTemplateRequest
//
// Update schedule-streams-job template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route GET /templates/{projectId}/schedule-streams-job/{templateId} template postStreamsJobTemplateRequest
//
// Get schedule-streams-job template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route DELETE /templates/{projectId}/schedule-streams-job/{templateId} template postStreamsJobTemplateRequest
//
// Delete schedule-streams-job template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:parameters postStreamsJobTemplateRequest
type postStreamsJobTemplateParamsWrapper struct {
	// The request body
	// in:body
	Body types.StreamsJobTemplate

	// in: path
	// required: true
	ProjectId int `json:"projectId"`

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

