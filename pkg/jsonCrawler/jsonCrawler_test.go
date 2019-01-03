package jsonCrawler

import (
	"context"
	"encoding/json"
	"testing"

	types "github.com/Microsoft/presidio-genproto/golang"
)

func analyzeFuncMock(ctx context.Context, text string, template *types.AnalyzeTemplate) ([]*types.AnalyzeResult, error) {
	return []*types.AnalyzeResult{
		&types.AnalyzeResult{},
	}, nil
}

func anonymizeFuncMock(ctx context.Context, analyzeResults []*types.AnalyzeResult, text string, anonymizeTemplate *types.AnonymizeTemplate) (*types.AnonymizeResponse, error) {
	var anonymized string
	for _, result := range analyzeResults {
		switch result.Field.Name {
		case "PERSON":
			anonymized = "<PERSON>"

		case "PHONE_NUMBER":
			anonymized = "<PHONE_NUMBER>"
		}
	}

	return &types.AnonymizeResponse{
		Text: anonymized,
	}, nil
}

func TestScanJsonWithSimple(t *testing.T) {
	// Arrange
	jsonSchema, _ := unmarshalJSON(`{"patients":[{
		"Name":"<PERSON>",
		"PhoneNumber":"<PHONE_NUMBER>"
	}]}`)

	jsonToAnonymize, _ := unmarshalJSON(`{"patients":[
		{
			"Name": "David Johnson",
			"PhoneNumber": "(212) 555-1234"
		},
		{
			"Name": "David Johnson",
			"PhoneNumber": "(212) 555-1234"
		}
	]}`)

	crawler := New(context.Background(), analyzeFuncMock, anonymizeFuncMock, &types.AnalyzeTemplate{}, &types.AnonymizeTemplate{})

	// Act
	crawler.ScanJson(jsonSchema, jsonToAnonymize)

	// Assert
	// for index := 0; index < len(jsonToAnonymize["patients"]); index++ {
	// 	assert.Equal(t, jsonToAnonymize["Name"], "<PERSON>")
	// 	assert.Equal(t, jsonToAnonymize["PhoneNumber"], "<PHONE_NUMBER>")
	// }
}

func unmarshalJSON(str string) (map[string]interface{}, error) {
	jsonMap := map[string]interface{}{}

	// Parsing/Unmarshalling JSON encoding/json
	err := json.Unmarshal([]byte(str), &jsonMap)
	if err != nil {
		return nil, err
	}

	return jsonMap, nil
}
