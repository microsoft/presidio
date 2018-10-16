package transformations

import (
	"fmt"

	types "github.com/Microsoft/presidio-genproto/golang"
)

//MaskValue ...
func MaskValue(text string, location types.Location, replaceWith string, charsToReplace int32, fromEnd bool) (string, error) {
	charsToReplaceInt := int(charsToReplace)
	if location.Length == 0 {
		location.Length = location.End - location.Start
	}
	pos := location.Start + location.Length
	if int32(len(text)) < pos {
		return "", fmt.Errorf("Indexes for values: are out of bounds")
	}
	if int32(len(replaceWith)) != 1 {
		return "", fmt.Errorf("Replace Char should be single")
	}
	runeReplaceWith := []rune(replaceWith)[0]
	runeText := []rune(text)
	before := runeText[:location.Start]
	after := runeText[pos:]
	curValue := string(runeText[location.Start:pos])
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

	return string(runeText), nil
}
