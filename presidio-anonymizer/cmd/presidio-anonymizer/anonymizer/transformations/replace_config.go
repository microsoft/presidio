package transformations

import (
	"errors"

	types "github.com/Microsoft/presidio-genproto/golang"
)

//ReplaceValue ...
func ReplaceValue(text string, location types.Location, newValue string) (string, error) {
	if location.Length == 0 {
		location.Length = location.End - location.Start
	}
	pos := location.Start + location.Length
	if int32(len(text)) < pos {
		return "", errors.New("Indexes for values: are out of bounds")
	}
	runeText := []rune(text)

	before := runeText[:location.Start]
	after := runeText[pos:]
	concat := string(before) + newValue + string(after)
	runeText = []rune(concat)
	return string(runeText), nil
}
