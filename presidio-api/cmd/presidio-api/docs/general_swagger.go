package docs

import types "github.com/Microsoft/presidio-genproto/golang"

// swagger:route GET /fieldTypes fields getFieldTypes
//
// Get all available field types
//
// responses:
//   200: getFieldTypesResponse

// The response including a list of field types
// swagger:response getFieldTypesResponse
type fieldTypesResponseWrapper struct {
	// in:body
	Types []types.FieldTypes
}
