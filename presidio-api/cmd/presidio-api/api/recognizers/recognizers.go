package recognizers

import (
	"context"

	types "github.com/Microsoft/presidio-genproto/golang"

	store "github.com/Microsoft/presidio/presidio-api/cmd/presidio-api/api"
)

//InsertRecognizer Inserts a new custom pattern recognizer via the Recognizer
// store service
func InsertRecognizer(ctx context.Context,
	api *store.API,
	request *types.RecognizerInsertOrUpdateRequest) (
	*types.RecognizersStoreResponse, error) {
	return api.Services.InsertRecognizer(ctx, request.Value)
}

// UpdateRecognizer updates an existing recognizer via the Recognizer
// store service
func UpdateRecognizer(ctx context.Context,
	api *store.API,
	request *types.RecognizerInsertOrUpdateRequest) (
	*types.RecognizersStoreResponse, error) {
	return api.Services.UpdateRecognizer(ctx, request.Value)
}

// DeleteRecognizer deletes an existing recognizer via the Recognizer
// store service
func DeleteRecognizer(ctx context.Context,
	api *store.API,
	request *types.RecognizerDeleteRequest) (
	*types.RecognizersStoreResponse, error) {
	return api.Services.DeleteRecognizer(ctx, request.Name)
}

// GetRecognizer retrieves an existing recognizer via the Recognizer
// store service
func GetRecognizer(ctx context.Context,
	api *store.API,
	request *types.RecognizerGetRequest) (
	*types.RecognizersGetResponse, error) {
	return api.Services.GetRecognizer(ctx, request.Name)
}

// GetAllRecognizers retrieves all existing recognizers via the Recognizer
// store service
func GetAllRecognizers(ctx context.Context,
	api *store.API,
	request *types.RecognizersGetAllRequest) (
	*types.RecognizersGetResponse, error) {
	return api.Services.GetAllRecognizers(ctx)
}

// GetUpdateTimeStamp returns the timestamp when the store was changed
func GetUpdateTimeStamp(ctx context.Context,
	api *store.API,
	request *types.RecognizerGetTimestampRequest) (
	*types.RecognizerTimestampResponse, error) {
	return api.Services.GetUpdateTimeStamp(ctx)
}
