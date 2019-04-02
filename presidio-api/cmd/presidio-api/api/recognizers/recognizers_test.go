package recognizers

import (
	"context"
	"encoding/json"

	"github.com/stretchr/testify/assert"

	types "github.com/Microsoft/presidio-genproto/golang"
	"github.com/Microsoft/presidio/pkg/presidio/services"

	store "github.com/Microsoft/presidio/presidio-api/cmd/presidio-api/api"
	"github.com/Microsoft/presidio/presidio-api/cmd/presidio-api/api/mocks"

	"testing"
)

func setupMockServices() *store.API {
	srv := &services.Services{
		AnalyzerService:  mocks.GetAnalyzeServiceMock(mocks.GetAnalyzerMockResult()),
		AnonymizeService: mocks.GetAnonymizerServiceMock(mocks.GetAnonymizerMockResult()),
		RecognizersStoreService: mocks.GetRecognizersStoreServiceMock(
			mocks.GetRecognizersStoreGetMockResult(),
			mocks.GetRecognizersStoreGetAllMockResult(),
			mocks.GetRecognizersStoreInsertOrUpdateMockResult(),
			mocks.GetRecognizersStoreDeleteMockResult(),
			mocks.GetRecognizersStoreGetHashMockResult()),
	}

	api := &store.API{
		Services:  srv,
		Templates: mocks.GetTemplateMock(),
	}
	return api
}

func createInsertOrUpdateRequest() types.RecognizerInsertOrUpdateRequest {
	// Insert a new pattern recognizer
	p := &types.Pattern{}
	p.Score = 0.123
	p.Regex = "*FindMe*"
	p.Name = "findme"
	patternArr := []*types.Pattern{}
	patternArr = append(patternArr, p)

	r := types.RecognizerInsertOrUpdateRequest{}
	newRecognizer := types.PatternRecognizer{
		Name:     "DemoRecognizer1",
		Patterns: patternArr,
		Entity:   "DEMO_ITEMS",
		Language: "en"}
	r.Value = &newRecognizer
	return r
}

func TestInsertRecognizer(t *testing.T) {

	api := setupMockServices()

	r := createInsertOrUpdateRequest()
	_, err := InsertRecognizer(context.Background(), api, &r)

	assert.NoError(t, err)
}

func TestUpdateRecognizer(t *testing.T) {

	api := setupMockServices()

	r := createInsertOrUpdateRequest()
	_, err := UpdateRecognizer(context.Background(), api, &r)

	assert.NoError(t, err)
}

func TestDeleteRecognizer(t *testing.T) {

	api := setupMockServices()

	r := types.RecognizerDeleteRequest{Name: "myname"}
	_, err := DeleteRecognizer(context.Background(), api, &r)

	assert.NoError(t, err)
}

func TestGetRecognizer(t *testing.T) {

	api := setupMockServices()

	r := types.RecognizerGetRequest{Name: "myname"}
	results, err := GetRecognizer(context.Background(), api, &r)

	assert.NoError(t, err)
	mockResult := mocks.GetRecognizersStoreGetMockResult().Recognizers
	bytesExpectedRecognizers, _ := json.Marshal(mockResult)
	assert.Equal(t, string(bytesExpectedRecognizers), results)
	// Verify single result

	var recognizers []types.PatternRecognizer
	json.Unmarshal([]byte(results), &recognizers)

	assert.Equal(t, 1, len(recognizers))
}

func TestGetAllRecognizer(t *testing.T) {

	api := setupMockServices()

	r := types.RecognizersGetAllRequest{}
	results, err := GetAllRecognizers(context.Background(), api, &r)

	assert.NoError(t, err)
	mockResult := mocks.GetRecognizersStoreGetAllMockResult().Recognizers
	bytesExpectedRecognizers, _ := json.Marshal(mockResult)
	assert.Equal(t, string(bytesExpectedRecognizers), results)

	// Verify multiple results
	recognizers := []types.PatternRecognizer{}
	json.Unmarshal([]byte(results), &recognizers)
	assert.Equal(t, 2, len(recognizers))
}
