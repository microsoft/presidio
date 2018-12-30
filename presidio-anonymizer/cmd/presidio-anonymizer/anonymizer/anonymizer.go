package anonymizer

import (
	"fmt"
	"sort"

	types "github.com/Microsoft/presidio-genproto/golang"

	methods "github.com/Microsoft/presidio/presidio-anonymizer/cmd/presidio-anonymizer/anonymizer/transformations"
)

type sortedResults []*types.AnalyzeResult

func (a sortedResults) Len() int      { return len(a) }
func (a sortedResults) Swap(i, j int) { a[i], a[j] = a[j], a[i] }
func (a sortedResults) Less(i, j int) bool {
	if a[i].Location.Start < a[j].Location.Start {
		return true
	}
	if a[i].Location.Start > a[j].Location.Start {
		return false
	}
	return a[i].Score > a[j].Score
}

//AnonymizeText ...
func AnonymizeText(text string, results []*types.AnalyzeResult, template *types.AnonymizeTemplate) (string, error) {

	//Sort results by start location to verify order
	sort.Sort(sortedResults(results))

	//Remove duplicates based on score
	if len(results) > 1 {
		results = removeDuplicatesBaseOnScore(results)
	}

	//Apply new values
	var err error
	for i := len(results) - 1; i >= 0; i-- {

		result := results[i]
		transformed := false
		for _, transformations := range template.FieldTypeTransformations {
			if transformed {
				break
			}
			if transformations.Fields == nil {
				text, err = transformField(transformations.Transformation, result, text)
				if err != nil {
					return "", err
				}
				break
			}

			for _, fieldType := range transformations.Fields {
				if fieldType.Name == result.Field.Name {
					text, err = transformField(transformations.Transformation, result, text)
					if err != nil {
						return "", err
					}
					transformed = true
					break
				}
			}
		}
	}

	return text, nil
}

func removeDuplicatesBaseOnScore(results []*types.AnalyzeResult) []*types.AnalyzeResult {

	j := 0
	for i := 1; i < len(results); i++ {
		if results[j].Location.Start == results[i].Location.Start && results[j].Location.End == results[i].Location.End {
			continue
		}
		j++

		// Swap
		results[i], results[j] = results[j], results[i]
	}

	return results[:j+1]
}

func transformField(transformation *types.Transformation, result *types.AnalyzeResult, text string) (string, error) {

	if transformation.ReplaceValue != nil {
		result, err := methods.ReplaceValue(text, *result.Location, transformation.ReplaceValue.NewValue)
		return result, err
	}
	if transformation.RedactValue != nil {
		result, err := methods.RedactValue(text, *result.Location, " ")
		return result, err
	}
	if transformation.HashValue != nil {
		result, err := methods.HashValue(text, *result.Location)
		return result, err
	}
	if transformation.MaskValue != nil {
		result, err := methods.MaskValue(text, *result.Location, transformation.MaskValue.MaskingCharacter, transformation.MaskValue.CharsToMask, transformation.MaskValue.FromEnd)
		return result, err
	}

	if transformation.FPEValue != nil {
		result, err := methods.FPEValue(text, *result.Location, transformation.FPEValue.Key, transformation.FPEValue.Tweak, transformation.FPEValue.Decrypt)
		return result, err
	}
	return "", fmt.Errorf("Transformation not found")
}
