package docs

import types "github.com/Microsoft/presidio-genproto/golang"

// swagger:route GET /analyzer/recognizers/{id} analyzer getRecognizerRequest
//
// Get an existing recognizer
//
// responses:
//   200: recognizersGetResponse

// A Regognizer
// swagger:response recognizersGetResponse
type regognizerResponseWrapper struct {
	// in:body
	Body types.RecognizersGetResponse
}

// swagger:parameters getRecognizerRequest
type regognizerParamsWrapper struct {
	// Recognizer name
	//
	// in: path
	// required: true
	Id string `json:"id"`
}

// swagger:route GET /analyzer/recognizers/ analyzer getAllRecognizersRequest
//
// Get all recognizers
//
// responses:
//   200: []allRecognizersGetResponse

// A a list of all recognizers
// swagger:response allRecognizersGetResponse
type allRegognizerResponseWrapper struct {
	// in:body
	Body []types.RecognizersGetResponse
}

// swagger:route POST /analyzer/recognizers/{id} analyzer insertRecognizerRequest
//
// Insert a new recognizer
//
// responses:
//   200: insertRecognizersResponse

// Insert new recognizer response
// swagger:response insertRecognizersResponse
type insertRegognizerResponseWrapper struct {
	// in: body
	Body string
}

// swagger:parameters insertRecognizerRequest
type insertRegognizerParamsWrapper struct {
	// Recognizer name
	//
	// in: path
	// required: true
	Id string `json:"id"`

	// Recognizer properties
	//
	// in: body
	Body types.RecognizerInsertOrUpdateRequest
}