package anonymizer

import (
	"sort"

	message_types "github.com/presidium-io/presidium-genproto/golang"
	methods "github.com/presidium-io/presidium/presidium-anonymizer/cmd/presidium-anonymizer/anonymizer/transformations"
)

type sortedResults []*message_types.AnalyzeResult

func (a sortedResults) Len() int           { return len(a) }
func (a sortedResults) Swap(i, j int)      { a[i], a[j] = a[j], a[i] }
func (a sortedResults) Less(i, j int) bool { return a[i].Location.Start < a[j].Location.Start }

//ApplyAnonymizerTemplate ...
func ApplyAnonymizerTemplate(text string, results []*message_types.AnalyzeResult, template *message_types.AnonymizeTemplate) (string, error) {

	relevantResults := findRelevantResultsToChange(results, template)

	//Sort results by start location to verify order
	sort.Sort(sortedResults(relevantResults))

	//Calculate relative locations of new values
	resultsTransformations := calculateLocations(relevantResults, template)

	//Apply new values
	for i, result := range relevantResults {

		transformation := resultsTransformations[i]

		if transformation.ReplaceValue != nil {
			err := methods.ReplaceValue(&text, *result.Location, transformation.NewValue)
			if err != nil {
				return "", err
			}
		}
		if transformation.RedactValue != nil {
			err := methods.RedactValue(&text, *result.Location, transformation.NewValue)
			if err != nil {
				return "", err
			}
		}
	}

	return text, nil
}

//Find relevant results to change based on the template
func findRelevantResultsToChange(results []*message_types.AnalyzeResult, config *message_types.AnonymizeTemplate) []*message_types.AnalyzeResult {
	var relevantResults = make([]*message_types.AnalyzeResult, 0)

	if config.FieldTypeTransformations != nil {
		for _, transformations := range config.FieldTypeTransformations {
			//Apply to all fieldtypes
			if transformations.Fields == nil {
				relevantResults = results
				break //No more than one transformation per fieldtype
			} else {
				//Apply to selected fieldtypes
				for _, result := range results {
					for _, fieldType := range transformations.Fields {
						if fieldType.Name == result.Field.Name {
							relevantResults = append(relevantResults, result)
							break //No more than one transformation per fieldtype
						}
					}
				}
			}
		}
	}
	return relevantResults
}

func calculateLocations(results []*message_types.AnalyzeResult, config *message_types.AnonymizeTemplate) []*message_types.Transformation {

	var resultsTransformations = make([]*message_types.Transformation, len(results))
	var locations = make([]message_types.Location, len(results))

	// Assign new values
	for i, result := range results {
		for _, transformations := range config.FieldTypeTransformations {
			if transformations.Fields == nil {
				setValue(transformations.Transformation)
				resultsTransformations[i] = transformations.Transformation
				break
			}

			for _, fieldType := range transformations.Fields {
				if fieldType.Name == result.Field.Name {
					setValue(transformations.Transformation)
					resultsTransformations[i] = transformations.Transformation
					break
				}
			}
		}

		locations[i] = *result.Location
		results[i] = result
	}

	//Calculate new indexes
	for i := 0; i < len(locations); i++ {
		sliceLocations := locations[i:]
		newLocations := methods.CalculateNewIndexes(sliceLocations, int32(len(resultsTransformations[i].NewValue)))

		//Change returned locations in original array
		j := i
		for _, loc := range newLocations {
			locations[j] = loc
			j++
		}
		results[i].Location = &newLocations[0]
	}
	return resultsTransformations
}

func setValue(transformation *message_types.Transformation) {
	var value string
	if transformation.ReplaceValue != nil {
		value = transformation.ReplaceValue.NewValue
	}
	if transformation.RedactValue != nil {
		value = " "
	}
	transformation.NewValue = value

}
