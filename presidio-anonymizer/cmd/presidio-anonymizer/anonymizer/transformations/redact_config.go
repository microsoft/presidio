package transformations

import (
	types "github.com/microsoft/presidio-genproto/golang"
)

//RedactValue ...
func RedactValue(text string, location types.Location, newValue string) (string, error) {
	return ReplaceValue(text, location, newValue)
}
