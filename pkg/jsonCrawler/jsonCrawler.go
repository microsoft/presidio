package jsonCrawler

import (
	"context"
	"fmt"
	"regexp"

	types "github.com/Microsoft/presidio-genproto/golang"
)

type analyzeFunc func(ctx context.Context, text string, template *types.AnalyzeTemplate) ([]*types.AnalyzeResult, error)
type anonymizeFunc func(ctx context.Context, analyzeResults []*types.AnalyzeResult, text string, anonymizeTemplate *types.AnonymizeTemplate) (*types.AnonymizeResponse, error)

const errorMsg = "Schema Json and Json to Anonymize are not in the same json format"

//JSONCrawler for analyzing and anonymizing text
type JSONCrawler struct {
	analyzeItem       analyzeFunc
	anonymizeItem     anonymizeFunc
	ctx               context.Context
	analyzeTemplate   *types.AnalyzeTemplate
	anonymizeTemplate *types.AnonymizeTemplate
}

//New JSONCrawler
func New(ctx context.Context, analyze analyzeFunc, anonymize anonymizeFunc, analyzeTemplate *types.AnalyzeTemplate, anonymizeTemplate *types.AnonymizeTemplate) *JSONCrawler {
	return &JSONCrawler{
		analyzeItem:       analyze,
		anonymizeItem:     anonymize,
		ctx:               ctx,
		analyzeTemplate:   analyzeTemplate,
		anonymizeTemplate: anonymizeTemplate,
	}
}

// ScanJSON scan the json in DFS to get to all the nodes
func (jsonCrawler *JSONCrawler) ScanJSON(schemaMap map[string]interface{}, valuesMap map[string]interface{}) error {
	err := checkIfEmptyMap(schemaMap, valuesMap)
	if err != nil {
		return err
	}

	for key, val := range schemaMap {
		switch concreteVal := val.(type) {
		case map[string]interface{}:
			err := jsonCrawler.scanIfNotEmpty(valuesMap, key, val, "map")
			if err != nil {
				return err
			}

		case []interface{}:
			err := jsonCrawler.scanIfNotEmpty(valuesMap, key, val, "array")
			if err != nil {
				return err
			}
		default:
			newVal, err := checkIfKeyExistInMap(valuesMap, key)
			if err != nil {
				return err
			}
			anonymizedVal, err := jsonCrawler.analyzeAndAnonymizeJSON(fmt.Sprint(newVal), fmt.Sprint(concreteVal))
			if err != nil {
				return err
			}
			valuesMap[key] = anonymizedVal
		}
	}
	return nil
}

func (jsonCrawler *JSONCrawler) scanArray(schemaArray []interface{}, valuesArray []interface{}) error {
	err := checkIfEmptyArray(schemaArray, valuesArray)
	if err != nil {
		return err
	}

	i := 0
	for j := range valuesArray {
		if len(schemaArray) > 1 {
			i = j
		}

		val := schemaArray[i]
		switch concreteVal := val.(type) {
		case map[string]interface{}:
			err := jsonCrawler.ScanJSON(val.(map[string]interface{}), valuesArray[j].(map[string]interface{}))
			if err != nil {
				return err
			}
		case []interface{}:
			err := jsonCrawler.scanArray(val.([]interface{}), valuesArray[j].([]interface{}))
			if err != nil {
				return err
			}
		default:
			newVal, err := jsonCrawler.analyzeAndAnonymizeJSON(fmt.Sprint(valuesArray[j]), fmt.Sprint(concreteVal))
			if err != nil {
				return err
			}
			valuesArray[j] = newVal
		}
	}

	return nil
}

func (jsonCrawler *JSONCrawler) scanIfNotEmpty(valuesMap map[string]interface{}, key string, val interface{}, valType string) error {
	newVal, err := checkIfKeyExistInMap(valuesMap, key)
	if err != nil {
		return err
	}
	if valType == "map" {
		return jsonCrawler.ScanJSON(val.(map[string]interface{}), newVal.(map[string]interface{}))
	}

	return jsonCrawler.scanArray(val.([]interface{}), newVal.([]interface{}))
}

func (jsonCrawler *JSONCrawler) analyzeAndAnonymizeJSON(val string, field string) (string, error) {
	match, err := regexp.MatchString("<[A-Z]+(_*[A-Z]*)*>", field)
	if err != nil {
		return "", err
	}

	if match {
		for key := range types.FieldTypesEnum_value {
			fieldName := field[1 : len(field)-1]
			if key == fieldName {
				analyzeResults := buildAnalyzeResult(val, fieldName)
				return jsonCrawler.getAnonymizeResult(val, analyzeResults)
			}
		}
	}

	if field == "analyze" {
		analyzeResults, err := jsonCrawler.analyzeItem(jsonCrawler.ctx, val, jsonCrawler.analyzeTemplate)
		if err != nil {
			return "", err
		}
		return jsonCrawler.getAnonymizeResult(val, analyzeResults)
	}

	return val, nil
}

func (jsonCrawler *JSONCrawler) getAnonymizeResult(text string, analyzeResults []*types.AnalyzeResult) (string, error) {
	result, err := jsonCrawler.anonymizeItem(jsonCrawler.ctx, analyzeResults, text, jsonCrawler.anonymizeTemplate)
	if err != nil {
		return "", err
	}
	return result.Text, nil
}

func checkIfKeyExistInMap(valuesMap map[string]interface{}, key string) (interface{}, error) {
	if newVal, ok := valuesMap[key]; ok {
		return newVal, nil
	}
	return nil, fmt.Errorf(errorMsg)
}

func checkIfEmptyMap(schema map[string]interface{}, json map[string]interface{}) error {
	if json == nil || schema == nil || len(json) == 0 {
		return fmt.Errorf(errorMsg)
	}
	return nil
}

func checkIfEmptyArray(schema []interface{}, json []interface{}) error {
	if json == nil || schema == nil || len(json) == 0 {
		return fmt.Errorf(errorMsg)
	}
	return nil
}

func buildAnalyzeResult(text string, field string) []*types.AnalyzeResult {
	return [](*types.AnalyzeResult){
		&types.AnalyzeResult{
			Text: text,
			Field: &types.FieldTypes{
				Name: field,
			},
			Score: 1,
			Location: &types.Location{
				Start: 0,
				End:   int32(len(text)),
			},
		},
	}
}
