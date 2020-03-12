package docs

import types "github.com/Microsoft/presidio-genproto/golang"

// swagger:route GET /templates/{projectID}/analyze/{templateID} template analyze getAnalyzeTemplate
//
// Get analyze template
//
// responses:
//   200: getAnalyzeTemplateResponse
//   400: templateGeneralError


// swagger:route POST /templates/{projectID}/analyze/{templateID} template analyze postAnalyzeTemplate
//
// Create analyze template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route PUT /templates/{projectID}/analyze/{templateID} template analyze putAnalyzeTemplate
//
// Update analyze template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route DELETE /templates/{projectID}/analyze/{templateID} template analyze deleteAnalyzeTemplate
//
// Delete analyze template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// An analyze template
// swagger:response getAnalyzeTemplateResponse
type analyzeTemplateResponseWrapper struct {
	// in: body
	Body types.AnalyzeTemplate
}


// swagger:parameters postAnalyzeTemplate putAnalyzeTemplate
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



// swagger:route GET /templates/{projectID}/anonymize/{templateID} template anonymize getAnonymizeTemplate
//
// Get anonymize template
//
// responses:
//   200: getAnonymizeTemplateResponse
//   400: templateGeneralError


// swagger:route POST /templates/{projectID}/anonymize/{templateID} template anonymize postAnonymizeTemplate
//
// Create anonymize template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route PUT /templates/{projectID}/anonymize/{templateID} template anonymize putAnonymizeTemplate
//
// Update anonymize template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route DELETE /templates/{projectID}/anonymize/{templateID} template anonymize deleteAnonymizeTemplate
//
// Delete anonymize template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// An anonymize template
// swagger:response getAnonymizeTemplateResponse
type anonymizeTemplateResponseWrapper struct {
	// in: body
	Body types.AnonymizeTemplate
}

// swagger:parameters postAnonymizeTemplate putAnonymizeTemplate
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



// swagger:route GET /templates/{projectID}/anonymize-image/{templateID} template anonymize-image getAnonymizeImageTemplate
//
// Get anonymize-image template
//
// responses:
//   200: getAnonymizeImageTemplateResponse
//   400: templateGeneralError


// swagger:route POST /templates/{projectID}/anonymize-image/{templateID} template anonymize-image postAnonymizeImageTemplate
//
// Create anonymize-image template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route PUT /templates/{projectID}/anonymize-image/{templateID} template anonymize-image putAnonymizeImageTemplate
//
// Update anonymize-image template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route DELETE /templates/{projectID}/anonymize-image/{templateID} template anonymize-image deleteAnonymizeImageTemplate
//
// Delete anonymize-image template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// An anonymize image template
// swagger:response getAnonymizeImageTemplateResponse
type anonymizeImageTemplateResponseWrapper struct {
	// in: body
	Body types.AnonymizeImageTemplate
}

// swagger:parameters postAnonymizeImageTemplate putAnonymizeImageTemplate
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



// swagger:route GET /templates/{projectID}/scan/{templateID} template scan getScanTemplate
//
// Get scan template
//
// responses:
//   200: getScanTemplateResponse
//   400: templateGeneralError


// swagger:route POST /templates/{projectID}/scan/{templateID} template scan postScanTemplate
//
// Create scan template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route PUT /templates/{projectID}/scan/{templateID} template scan putScanTemplate
//
// Update scan template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route DELETE /templates/{projectID}/scan/{templateID} template scan deleteScanTemplate
//
// Delete scan template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// A scan template
// swagger:response getScanTemplateResponse
type scanTemplateResponseWrapper struct {
	// in: body
	Body types.ScanTemplate
}

// swagger:parameters postScanTemplate putScanTemplate
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



// swagger:route GET /templates/{projectID}/stream/{templateID} template stream getStreamTemplate
//
// Get stream template
//
// responses:
//   200: getStreamTemplateResponse
//   400: templateGeneralError


// swagger:route POST /templates/{projectID}/stream/{templateID} template stream postStreamTemplate
//
// Create stream template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route PUT /templates/{projectID}/stream/{templateID} template stream putStreamTemplate
//
// Update stream template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route DELETE /templates/{projectID}/stream/{templateID} template stream deleteStreamTemplate
//
// Delete stream template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// A stream template
// swagger:response getStreamTemplateResponse
type streamTemplateResponseWrapper struct {
	// in: body
	Body types.StreamTemplate
}

// swagger:parameters postStreamTemplate putStreamTemplate
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




// swagger:route GET /templates/{projectID}/datasink/{templateID} template datasink getDatasinkTemplate
//
// Get datasink template
//
// responses:
//   200: getDatasinkTemplateResponse
//   400: templateGeneralError


// swagger:route POST /templates/{projectID}/datasink/{templateID} template datasink postDatasinkTemplate
//
// Create datasink template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route PUT /templates/{projectID}/datasink/{templateID} template datasink putDatasinkTemplate
//
// Update datasink template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route DELETE /templates/{projectID}/datasink/{templateID} template datasink deleteDatasinkTemplate
//
// Delete datasink template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// A Datasink template
// swagger:response getDatasinkTemplateResponse
type datasinkTemplateResponseWrapper struct {
	// in: body
	Body types.DatasinkTemplate
}

// swagger:parameters postDatasinkTemplate putDatasinkTemplate
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



// swagger:route GET /templates/{projectID}/schedule-scanner-cronjob/{templateID} template schedule-scanner-cronjob getScannerCronJobTemplate
//
// Get schedule-scanner-cronjob template
//
// responses:
//   200: getScannerCronJobTemplateResponse
//   400: templateGeneralError


// swagger:route POST /templates/{projectID}/schedule-scanner-cronjob/{templateID} template schedule-scanner-cronjob postScannerCronJobTemplate
//
// Create schedule-scanner-cronjob template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route PUT /templates/{projectID}/schedule-scanner-cronjob/{templateID} template schedule-scanner-cronjob putScannerCronJobTemplate
//
// Update schedule-scanner-cronjob template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route DELETE /templates/{projectID}/schedule-scanner-cronjob/{templateID} template schedule-scanner-cronjob deleteScannerCronJobTemplate
//
// Delete schedule-scanner-cronjob template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// A ScannerCronJob template
// swagger:response getScannerCronJobTemplateResponse
type scannerCronJobTemplateResponseWrapper struct {
	// in: body
	Body types.ScannerCronJobTemplate
}

// swagger:parameters postScannerCronJobTemplate putScannerCronJobTemplate
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



// swagger:route GET /templates/{projectID}/schedule-streams-job/{templateID} template schedule-streams-job getStreamsJobTemplate
//
// Get schedule-streams-job template
//
// responses:
//   200: getStreamsJobTemplateResponse
//   400: templateGeneralError


// swagger:route POST /templates/{projectID}/schedule-streams-job/{templateID} template schedule-streams-job postStreamsJobTemplate
//
// Create schedule-streams-job template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route PUT /templates/{projectID}/schedule-streams-job/{templateID} template schedule-streams-job putStreamsJobTemplate
//
// Update schedule-streams-job template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// swagger:route DELETE /templates/{projectID}/schedule-streams-job/{templateID} template schedule-streams-job deleteStreamsJobTemplate
//
// Delete schedule-streams-job template
//
// responses:
//   200: templateGeneralResponse
//   400: templateGeneralError


// A Streams Job template
// swagger:response getStreamsJobTemplateResponse
type streamsJobTemplateResponseWrapper struct {
	// in: body
	Body types.StreamsJobTemplate
}

// swagger:parameters postStreamsJobTemplate putStreamsJobTemplate
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


// swagger:parameters getStreamsJobTemplate deleteStreamsJobTemplate getScannerCronJobTemplate deleteScannerCronJobTemplate getDatasinkTemplate deleteDatasinkTemplate getStreamTemplate deleteStreamTemplate getScanTemplate deleteScanTemplate getAnonymizeImageTemplate deleteAnonymizeImageTemplate getAnonymizeTemplate deleteAnonymizeTemplate getAnalyzeTemplate deleteAnalyzeTemplate
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

