package transformations

import (
	message_types "github.com/presid-io/presidio-genproto/golang"
)

//RedactValue ...
func RedactValue(text string, location message_types.Location, newValue string) (string, error) {
	return ReplaceValue(text, location, newValue)
}
