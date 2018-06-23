package anonymizer

import (
	"sort"

	message_types "github.com/presidium-io/presidium/pkg/types"
	methods "github.com/presidium-io/presidium/presidium-anonymizer/cmd/presidium-anonymizer/anonymizer/transformations"
)

type sortedResults []*message_types.Result

func (a sortedResults) Len() int           { return len(a) }
func (a sortedResults) Swap(i, j int)      { a[i], a[j] = a[j], a[i] }
func (a sortedResults) Less(i, j int) bool { return a[i].Location.Start < a[j].Location.Start }

//ApplyAnonymizerTemplate ...
func ApplyAnonymizerTemplate(text string, results []*message_types.Result, template *message_types.AnonymizeTemplate) (string, error) {

	config := template.Configuration

	relevantResults := findRelevantResultsToChange(results, config)

	//Sort results by start location to verify order
	sort.Sort(sortedResults(relevantResults))

	//Calculate relative locations of new values
	calculateLocations(relevantResults, *config)

	//Apply new values
	for _, result := range relevantResults {

		if result.Transformation.ReplaceValue != nil {
			err := methods.ReplaceValue(&text, *result.Location, result.Transformation.NewValue)
			if err != nil {
				return "", err
			}
		}
		if result.Transformation.RedactValue != nil {
			err := methods.RedactValue(&text, *result.Location, result.Transformation.NewValue)
			if err != nil {
				return "", err
			}
		}
	}

	return text, nil
}

//Find relevant results to change based on the template
func findRelevantResultsToChange(results []*message_types.Result, config *message_types.Configuration) []*message_types.Result {
	var relevantResults = make([]*message_types.Result, 0)

	if config.FieldTypeTransformations != nil {
		for _, transformations := range config.FieldTypeTransformations {
			//Apply to all fieldtypes
			if transformations.FieldTypes == nil {
				relevantResults = results
				break //No more than one transformation per fieldtype
			} else {
				//Apply to selected fieldtypes
				for _, result := range results {
					for _, fieldType := range transformations.FieldTypes {
						if fieldType.Name == result.FieldType {
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

func calculateLocations(results []*message_types.Result, config message_types.Configuration) {

	var locations = make([]message_types.Location, len(results))

	for i, result := range results {
		for _, transformations := range config.FieldTypeTransformations {
			if transformations.FieldTypes == nil {

				setValue(transformations.Transformation)
				result.Transformation = transformations.Transformation
				break
			}

			for _, fieldType := range transformations.FieldTypes {
				if fieldType.Name == result.FieldType {
					setValue(transformations.Transformation)
					result.Transformation = transformations.Transformation
					break
				}
			}
		}

		locations[i] = *result.Location
		results[i] = result
	}

	for i := 0; i < len(locations); i++ {
		sliceLocations := locations[i:]

		newLocations := methods.CalculateNewIndexes(sliceLocations, int32(len(results[i].Transformation.NewValue)))

		//Change returned locations in original array
		j := i
		for _, loc := range newLocations {
			locations[j] = loc
			j++
		}
		results[i].Location = &newLocations[0]
	}
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
