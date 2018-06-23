package transformations

import (
	"fmt"

	types "github.com/Microsoft/presidio-genproto/golang"
)

//ReplaceValue ...
func ReplaceValue(text string, location types.Location, newValue string) (string, error) {
	if location.Length == 0 {
		location.Length = location.End - location.Start
	}
	pos := location.Start + location.Length
	if int32(len(text)) < pos {
		return "", fmt.Errorf("Indexes for values: are out of bounds")
	}
	new := replaceValueInString(text, newValue, int(location.Start), int(pos))
	return new, nil
}
