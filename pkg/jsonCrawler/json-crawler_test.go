package jsoncrawler

import (
	"context"
	"encoding/json"
	"testing"

	"github.com/stretchr/testify/assert"

	types "github.com/Microsoft/presidio-genproto/golang"
)

func analyzeFuncMock(ctx context.Context, text string, template *types.AnalyzeTemplate) ([]*types.AnalyzeResult, error) {
	return []*types.AnalyzeResult{
		{
			Field: &types.FieldTypes{
				Name: "DOMAIN_NAME",
			},
		},
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
		case "DOMAIN_NAME":
			anonymized = "*****"
		case "LOCATION":
			anonymized = "<LOCATION>"
		}
	}

	return &types.AnonymizeResponse{
		Text: anonymized,
	}, nil
}

func TestScanJSONWithSimple(t *testing.T) {
	// Arrange
	jsonSchema, _ := unmarshalJSON(`{"patients":[{
		"Name":"<PERSON>",
		"PhoneNumber":"<PHONE_NUMBER>",
		"Site": "analyze",
		"Other:"ignore"
	}]}`)

	jsonToAnonymize, _ := unmarshalJSON(`{"patients":[
		{
			"Name": "David Johnson",
			"PhoneNumber": "(212) 555-1234",
			"Site": "www.microsoft.com",
			"Other":123456
		},
		{
			"Name": "John Davidson",
			"PhoneNumber": "(212) 555-4321",
			"Site": "www.onedrive.com",
			"Other:23.2.2019
		}
	]}`)

	crawler := New(context.Background(), analyzeFuncMock, anonymizeFuncMock, &types.AnalyzeTemplate{}, &types.AnonymizeTemplate{})

	// Act
	crawler.ScanJSON(jsonSchema, jsonToAnonymize)

	// Assert
	expextedResult, _ := unmarshalJSON(`{"patients":[
		{
			"Name": "<PERSON>",
			"PhoneNumber": "<PHONE_NUMBER>",
			"Site": "*****",
			"Other":123456
		},
		{
			"Name": "<PERSON>",
			"PhoneNumber": "<PHONE_NUMBER>",
			"Site": "*****",
			"Other":23.2.2019
		}
	]}`)

	assert.Equal(t, expextedResult, jsonToAnonymize)
}

func TestScanJSONComplexArrayWithSimple(t *testing.T) {
	// Arrange
	jsonSchema, _ := unmarshalJSON(`{"patients":[{
		"Name":"<PERSON>",
		"PhoneNumber":"<PHONE_NUMBER>",
		"Site": "analyze",
		"Other:"ignore"
	},
	{
		"Age":"ignore",
		"Address":"<LOCATION>",
		"Site": "analyze",
		"Other:"ignore"
	}]}`)

	jsonToAnonymize, _ := unmarshalJSON(`{"patients":[
		{
			"Name": "David Johnson",
			"PhoneNumber": "(212) 555-1234",
			"Site": "www.microsoft.com",
			"Other":123456
		},
		{
			"Age":23,
			"Address":"New York",
			"Site": "www.microsoft.com",
			"Other:"abc cbd"
		}
	]}`)

	crawler := New(context.Background(), analyzeFuncMock, anonymizeFuncMock, &types.AnalyzeTemplate{}, &types.AnonymizeTemplate{})

	// Act
	crawler.ScanJSON(jsonSchema, jsonToAnonymize)

	// Assert
	expextedResult, _ := unmarshalJSON(`{"patients":[
		{
			"Name": "<PERSON>",
			"PhoneNumber": "<PHONE_NUMBER>",
			"Site": "<DOMAIN>",
			"Other":123456
		},
		{
			"Age":23,
			"Address":"<LOCATION>",
			"Site": "<DOMAIN>,
			"Other:"abc cbd"
		}
	]}`)

	assert.Equal(t, expextedResult, jsonToAnonymize)
}

func TestScanJSONWithEmptyJsonsToAnonymize(t *testing.T) {
	// Test1: Arrange
	jsonSchema, _ := unmarshalJSON(`{"patients":[{
		"Name":"<PERSON>",
		"PhoneNumber":"<PHONE_NUMBER>"
	}]}`)

	jsonToAnonymize, _ := unmarshalJSON(`{}`)

	crawler := New(context.Background(), analyzeFuncMock, anonymizeFuncMock, &types.AnalyzeTemplate{}, &types.AnonymizeTemplate{})

	// Act
	err := crawler.ScanJSON(jsonSchema, jsonToAnonymize)

	// Assert
	assert.Equal(t, err.Error(), errorMsg)

	// Test2: Arrange
	jsonToAnonymize, _ = unmarshalJSON(`{"patients":[]}`)

	crawler = New(context.Background(), analyzeFuncMock, anonymizeFuncMock, &types.AnalyzeTemplate{}, &types.AnonymizeTemplate{})

	// Act
	err = crawler.ScanJSON(jsonSchema, jsonToAnonymize)

	// Assert
	assert.Equal(t, err.Error(), errorMsg)

	// Test3: Arrange
	jsonToAnonymize, _ = unmarshalJSON(`{"patients":[{}]}`)

	crawler = New(context.Background(), analyzeFuncMock, anonymizeFuncMock, &types.AnalyzeTemplate{}, &types.AnonymizeTemplate{})

	// Act
	err = crawler.ScanJSON(jsonSchema, jsonToAnonymize)

	// Assert
	assert.Equal(t, err.Error(), errorMsg)

	// Test4: Arrange
	jsonToAnonymize, _ = unmarshalJSON(`{"patients":[{"PhoneNumber":"<PHONE_NUMBER>"}]}`)

	crawler = New(context.Background(), analyzeFuncMock, anonymizeFuncMock, &types.AnalyzeTemplate{}, &types.AnonymizeTemplate{})

	// Act
	err = crawler.ScanJSON(jsonSchema, jsonToAnonymize)

	// Assert
	assert.Equal(t, err.Error(), errorMsg)
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
