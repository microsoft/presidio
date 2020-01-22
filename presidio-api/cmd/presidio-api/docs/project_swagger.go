package docs

import types "github.com/Microsoft/presidio-genproto/golang"

// swagger:route POST /projects/{projectId}/analyze analyze analyzeRequest
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
	ProjectId int `json:"projectId"`
}


// swagger:route POST /projects/{projectId}/anonymize anonymize anonymizeRequest
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
	ProjectId int `json:"projectId"`
}