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
}
