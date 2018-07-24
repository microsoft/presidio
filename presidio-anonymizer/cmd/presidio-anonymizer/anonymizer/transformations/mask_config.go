package transformations

import (
	"errors"

	message_types "github.com/presid-io/presidio-genproto/golang"
)

//MaskValue ...
func MaskValue(text *string, location message_types.Location, replaceWith string, charsToReplace int32, fromEnd bool) error {
	charsToReplaceInt := int(charsToReplace)
	pos := location.NewStart + location.Length
	if int32(len(*text)) < pos {
		return errors.New("Indexes for values: are out of bounds")
	}
	if int32(len(replaceWith)) != 1 {
		return errors.New("Replace Char should be single")
	}
	runeReplaceWith := []rune(replaceWith)[0]
	runeText := []rune(*text)
	before := runeText[:location.NewStart]
	after := runeText[pos:]
	curValue := string(runeText[location.NewStart:pos])
	if charsToReplaceInt > len(curValue) {
		charsToReplaceInt = len(curValue)
	}
	runeCur := []rune(curValue)
	if !fromEnd {
		for i := 0; i < charsToReplaceInt; i++ {
			runeCur[i] = runeReplaceWith
		}
	} else {
		for i := len(curValue) - 1; i > len(curValue)-1-charsToReplaceInt; i-- {
			runeCur[i] = runeReplaceWith
		}
	}
	concat := string(before) + string(runeCur) + string(after)
	runeText = []rune(concat)
	*text = string(runeText)
	return nil
}
