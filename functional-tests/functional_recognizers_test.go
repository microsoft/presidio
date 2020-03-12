// +build functional

package tests

import (
	"encoding/json"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"

	types "github.com/Microsoft/presidio-genproto/golang"
	"github.com/Microsoft/presidio/functional-tests/common"
)

// TestAddRecognizerAndAnalyze tests the custom recognizers logic.
// 1) It add a new custom recognizer and then use it to
// to analyze text
// 2) Updates the recognizer and verify the new version is used
// 3) Delete the recognizer and verify the results
func TestAddRecognizerAndAnalyze(t *testing.T) {
	// Add a custom recognizer and use it
	payload := common.GeneratePayload("new-custom-pattern-recognizer.json")
	common.InvokeHTTPRequest(t, "/api/v1/analyzer/recognizers/newrec1", "POST", payload)

	payload = common.GeneratePayload("analyze-custom-recognizer-template.json")
	common.InvokeHTTPRequest(t, "/api/v1/templates/test/analyze/test-custom", "POST", payload)

	payload = common.GeneratePayload("analyze-custom-recognizer-request.json")
	results := common.InvokeHTTPRequest(t, "/api/v1/projects/test/analyze", "POST", payload)

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
				Start: 62, End: 69, Length: 7,
			},
		},
	}

	verifyResults(t, results, expectedResults)

	// sleeping to make sure the timestamp changes
	time.Sleep(2 * time.Second)

	// Update the recognizer and expect a new entity to be found
	updatePayload := common.GeneratePayload("update-custom-pattern-recognizer.json")
	common.InvokeHTTPRequest(t, "/api/v1/analyzer/recognizers/newrec1", "PUT", updatePayload)

	newAnalyzePayload := common.GeneratePayload("analyze-custom-recognizer-request.json")
	newResults := common.InvokeHTTPRequest(t, "/api/v1/projects/test/analyze", "POST", newAnalyzePayload)

	updatedExpectedResults := []*types.AnalyzeResult{
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
				Start: 42, End: 52, Length: 10,
			},
		},
		{
			Location: &types.Location{
				Start: 62, End: 69, Length: 7,
			},
		},
	}

	verifyResults(t, newResults, updatedExpectedResults)

	// sleeping to make sure the timestamp changes
	time.Sleep(2 * time.Second)

	// Now, delete this recognizer and expect all the 'rockets' not
	// to appear
	common.InvokeHTTPRequest(t, "/api/v1/analyzer/recognizers/newrec1", "DELETE", []byte(""))

	deletedAnalyzePayload := common.GeneratePayload("analyze-custom-recognizer-request.json")
	newResults = common.InvokeHTTPRequest(t, "/api/v1/projects/test/analyze", "POST", deletedAnalyzePayload)

	deletedExpectedResults := []*types.AnalyzeResult{
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
	}

	// Verify after the deletion no 'rockets' entities
	verifyResults(t, newResults, deletedExpectedResults)
}

func verifyResults(t *testing.T,
	returnedResults string, expectedResults []*types.AnalyzeResult) {

	returnedResult := []*types.AnalyzeResult{}
	err := json.Unmarshal([]byte(returnedResults), &returnedResult)
	assert.NoError(t, err)

	assert.Equal(t, len(expectedResults), len(returnedResult))
	// we don't know the exact order so we need to verify the results
	for _, expectedItem := range expectedResults {
		found := false
		for _, returnedItem := range returnedResult {
			if returnedItem.Location.Start == expectedItem.Location.Start &&
				returnedItem.Location.End == expectedItem.Location.End &&
				returnedItem.Location.Length == expectedItem.Location.Length {
				found = true
			}
		}
		assert.Equal(t, true, found)
	}
}
