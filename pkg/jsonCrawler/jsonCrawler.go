package jsonCrawler

import (
	"context"
	"fmt"
	"regexp"

	types "github.com/Microsoft/presidio-genproto/golang"
)

type analyzeFunc func(ctx context.Context, text string, template *types.AnalyzeTemplate) ([]*types.AnalyzeResult, error)
type anonymizeFunc func(ctx context.Context, analyzeResults []*types.AnalyzeResult, text string, anonymizeTemplate *types.AnonymizeTemplate) (*types.AnonymizeResponse, error)

//JSONCrawler
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

// ScanJson scan the json in DFS to get to all the nodes
func (jsonCrawler *JSONCrawler) ScanJson(schemaMap map[string]interface{}, valuesMap map[string]interface{}) error {
	for key, val := range schemaMap {
		switch concreteVal := val.(type) {
		case map[string]interface{}:
			err := jsonCrawler.ScanJson(val.(map[string]interface{}), (valuesMap[key]).(map[string]interface{}))
			if err != nil {
				return err
			}
		case []interface{}:
			err := jsonCrawler.scanArray(val.([]interface{}), (valuesMap[key]).([]interface{}))
			if err != nil {
				return err
			}
		default:
			newVal, err := jsonCrawler.analyzeAndAnonymizeJSON(fmt.Sprint(valuesMap[key]), fmt.Sprint(concreteVal))
			if err != nil {
				return err
			}
			valuesMap[key] = newVal
		}
	}
	return nil
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

func (jsonCrawler *JSONCrawler) scanArray(schemaArray []interface{}, valuesArray []interface{}) error {
	for _, val := range schemaArray {
		switch concreteVal := val.(type) {
		case map[string]interface{}:
			for j := range valuesArray {
				err := jsonCrawler.ScanJson(val.(map[string]interface{}), valuesArray[j].(map[string]interface{}))
				if err != nil {
					return err
				}
			}
		case []interface{}:
			for j := range valuesArray {
				err := jsonCrawler.scanArray(val.([]interface{}), valuesArray[j].([]interface{}))
				if err != nil {
					return err
				}
			}
		default:
			for j := range valuesArray {
				newVal, err := jsonCrawler.analyzeAndAnonymizeJSON(fmt.Sprint(valuesArray[j]), fmt.Sprint(concreteVal))
				if err != nil {
					return err
				}
				valuesArray[j] = newVal
			}
		}
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
