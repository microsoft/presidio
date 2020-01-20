package docs

import (
	"github.com/Microsoft/presidio/presidio-api/cmd/presidio-api/api"
)

// swagger:route POST /projects/{projectId}/analyze analyze analyze
//
// Analyze text
//
// responses:
//   200: analyzeResponse

// A response includes a list of recognized fields in the text to be anonymized.
// swagger:response analyzeResponse
type analyzeResponseWrapper struct {
	// in:body
	//
	Body struct {
	}
}

// swagger:parameters idOfFoobarEndpoint
type foobarParamsWrapper struct {
	// This text will appear as description of your request body.
	// in:body
	Body api.FooBarRequest
}
