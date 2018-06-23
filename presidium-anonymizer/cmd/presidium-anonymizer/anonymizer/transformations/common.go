package transformations

import (
	message_types "github.com/presidium-io/presidium/pkg/types"
)

//CalculateNewIndexes ...
func CalculateNewIndexes(locations []message_types.Location, valueLength int32) []message_types.Location {

	var offset int32

	// Calculate first element
	location := locations[0]
	location.Length = location.End - location.Start
	if location.NewStart == 0 {
		offset = valueLength - location.Length
		location.NewStart = location.Start
		location.NewEnd = location.End + offset
		location.NewLength = location.Length + offset
	} else {
		offset = valueLength - location.NewLength
		location.NewEnd = location.NewEnd + offset
		location.NewLength = location.NewLength + offset
	}
	locations[0] = location

	//Calculate remaining items offsets
	for i := 1; i < len(locations); i++ {
		if locations[i].NewStart == 0 {
			locations[i].NewStart = locations[i].Start + offset
			locations[i].NewEnd = locations[i].End + offset
		} else {
			locations[i].NewStart = locations[i].NewStart + offset
			locations[i].NewEnd = locations[i].NewEnd + offset
		}
		locations[i].NewLength = locations[i].NewEnd - locations[i].NewStart
	}

	return locations
}
