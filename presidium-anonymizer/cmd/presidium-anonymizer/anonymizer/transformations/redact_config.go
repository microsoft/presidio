package transformations

import (
	message_types "github.com/presidium-io/presidium-genproto/golang"
)

//RedactValue ...
func RedactValue(text *string, location message_types.Location, newValue string) error {
	return ReplaceValue(text, location, newValue)
}
