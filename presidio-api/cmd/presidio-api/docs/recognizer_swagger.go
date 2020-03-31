package docs

import types "github.com/Microsoft/presidio-genproto/golang"

// swagger:route GET /analyzer/recognizers/{id} analyze getRecognizer
//
// Get an existing recognizer
//
// responses:
//   200: getRecognizerResponse

// A Recognizer
// swagger:response getRecognizerResponse
type regognizerResponseWrapper struct {
	// in:body
	Body types.RecognizersGetResponse
}

// swagger:parameters getRecognizer
type regognizerParamsWrapper struct {
	// Recognizer name
	//
	// in: path
	// required: true
	ID string `json:"id"`
}

// swagger:route GET /analyzer/recognizers/ analyze getAllRecognizers
//
// Get all recognizers
//
// responses:
//   200: []getAllRecognizersResponse

// A a list of all recognizers
// swagger:response getAllRecognizersResponse
type allRegognizerResponseWrapper struct {
	// in:body
	Body []types.RecognizersGetResponse
}

// swagger:route POST /analyzer/recognizers/{id} analyze insertRecognizer
//
// Insert a new recognizer
//
// responses:
//   200: insertRecognizerResponse

// Insert new recognizer response
// swagger:response insertRecognizerResponse
type insertRegognizerResponseWrapper struct {
	// in: body
	Body string
}

// swagger:parameters insertRecognizer
type insertRegognizerParamsWrapper struct {
	// Recognizer name
	//
	// in: path
	// required: true
	ID string `json:"id"`

	// Recognizer properties
	//
	// in: body
	Body types.RecognizerInsertOrUpdateRequest
}