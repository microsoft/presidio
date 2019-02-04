package anonymizer

import (
	"fmt"
	"sort"
	"strings"

	types "github.com/Microsoft/presidio-genproto/golang"

	methods "github.com/Microsoft/presidio/presidio-anonymizer/cmd/presidio-anonymizer/anonymizer/transformations"
)

type sortedResults []*types.AnalyzeResult

// transformSingleField
func transformSingleField(transformation *types.Transformation, result *types.AnalyzeResult, text string) (bool, string, error) {
	newtext, err := transformField(transformation, result, text)
	if err != nil {
		return false, "", err
	}
	return true, newtext, nil
}

// anonymizeSingleResult anonymize a single analyze result
func anonymizeSingleResult(result *types.AnalyzeResult, transformations []*types.FieldTypeTransformation, text string) (bool, string, error) {
	for _, transformation := range transformations {
		if transformation.Fields == nil {
			return transformSingleField(transformation.Transformation, result, text)
		}

		for _, fieldType := range transformation.Fields {
			if fieldType.Name == result.Field.Name {
				return transformSingleField(transformation.Transformation, result, text)
			}
		}
	}

	return false, "", nil
}

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
	for i := len(results) - 1; i >= 0; i-- {

		result := results[i]
		transformed, transformedText, err := anonymizeSingleResult(result, template.FieldTypeTransformations, text)
		if err != nil {
			return "", err
		}

		if transformed {
			text = transformedText
			continue
		}

		// Now, for any analyzer result which wasn't transformed, either
		// transform using the default transformation, as described in the
		// template, or fallback to default transformation
		if template.DefaultTransformation != nil {
			text, err = transformField(template.DefaultTransformation, result, text)
		} else {
			text, err = methods.ReplaceValue(text, *result.Location, "<"+strings.ToUpper(result.Field.Name)+">")
		}
		if err != nil {
			return "", err
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
