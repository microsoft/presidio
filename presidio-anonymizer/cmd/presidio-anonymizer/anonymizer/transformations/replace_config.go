package transformations

import (
	"errors"

	message_types "github.com/presid-io/presidio-genproto/golang"
)

//ReplaceValue ...
func ReplaceValue(text *string, location message_types.Location, newValue string) error {

	pos := location.NewStart + location.Length
	if int32(len(*text)) < pos {
		return errors.New("Indexes for values: are out of bounds")
	}
	runeText := []rune(*text)

	before := runeText[:location.NewStart]
	after := runeText[pos:]
	concat := string(before) + newValue + string(after)
	runeText = []rune(concat)
	*text = string(runeText)
	return nil
}
