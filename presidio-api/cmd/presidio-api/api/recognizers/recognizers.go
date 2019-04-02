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
	request *types.RecognizerInsertOrUpdateRequest,
) (string, error) {
	_, err := api.Services.InsertRecognizer(ctx, request.Value)
	if err != nil {
		return "", err
	}
	return "Recognizer was inserted successfully", nil
}

// UpdateRecognizer updates an existing recognizer via the Recognizer
// store service
func UpdateRecognizer(ctx context.Context,
	api *store.API,
	request *types.RecognizerInsertOrUpdateRequest,
) (string, error) {
	_, err := api.Services.UpdateRecognizer(ctx, request.Value)
	if err != nil {
		return "", err
	}
	return "Recognizer was updated successfully", nil
}

// DeleteRecognizer deletes an existing recognizer via the Recognizer
// store service
func DeleteRecognizer(ctx context.Context,
	api *store.API,
	request *types.RecognizerDeleteRequest,
) (string, error) {
	_, err := api.Services.DeleteRecognizer(ctx, request.Name)
	if err != nil {
		return "", err
	}
	return "Recognizer was deleted successfully", nil
}

// GetRecognizer retrieves an existing recognizer via the Recognizer
// store service
func GetRecognizer(ctx context.Context,
	api *store.API,
	request *types.RecognizerGetRequest,
) ([]*types.PatternRecognizer, error) {
	res, err := api.Services.GetRecognizer(ctx, request.Name)
	if err != nil {
		return nil, err
	}

	return res.Recognizers, nil
}

// GetAllRecognizers retrieves all existing recognizers via the Recognizer
// store service
func GetAllRecognizers(ctx context.Context,
	api *store.API,
	request *types.RecognizersGetAllRequest,
) ([]*types.PatternRecognizer, error) {
	res, err := api.Services.GetAllRecognizers(ctx)
	if err != nil {
		return nil, err
	}

	return res.Recognizers, nil
}
