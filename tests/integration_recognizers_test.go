// +build functional

package tests

import (
	"encoding/json"
	"testing"

	"github.com/stretchr/testify/assert"

	types "github.com/Microsoft/presidio-genproto/golang"
	log "github.com/Microsoft/presidio/pkg/logger"
)

// TestAddRecognizerAndAnalyze add a new custom recognizer and then use it to
// to analyze text
func TestAddRecognizerAndAnalyze(t *testing.T) {
	payload := generatePayload("new-custom-pattern-recognizer.json")
	invokeHTTPRequest(t, "/api/v1/analyzer/recognizers/newrec1", "POST", payload)

	payload = generatePayload("analyze-custom-recognizer-template.json")
	invokeHTTPRequest(t, "/api/v1/templates/test/analyze/test-custom", "POST", payload)

	payload = generatePayload("analyze-custom-recognizer-request.json")
	resultsStr := invokeHTTPRequest(t, "/api/v1/projects/test/analyze", "POST", payload)
	log.Info(resultsStr)
	expectedResults := []*types.AnalyzeResult{
		{
			Location: &types.Location{
				Start: 7, End: 16, Length: 9,
			},
		},
		{
			Location: &types.Location{
				Start: 17, End: 24, Length: 7,
			},
		},
		{
			Location: &types.Location{
				Start: 28, End: 35, Length: 7,
			},
		},
		{
			Location: &types.Location{
				Start: 63, End: 69, Length: 6,
			},
		},
	}

	returnedResult := []*types.AnalyzeResult{}
	err := json.Unmarshal([]byte(resultsStr), &returnedResult)
	assert.NoError(t, err)
	assert.Equal(t, expectedResults[0].Location, returnedResult[0].Location)
	assert.Equal(t, expectedResults[1].Location, returnedResult[1].Location)
	assert.Equal(t, expectedResults[2].Location, returnedResult[2].Location)
	assert.Equal(t, expectedResults[3].Location, returnedResult[3].Location)
}
