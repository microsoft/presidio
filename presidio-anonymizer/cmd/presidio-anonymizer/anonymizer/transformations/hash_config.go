package transformations

import (
	"errors"
	"fmt"
	"hash/fnv"

	message_types "github.com/presid-io/presidio-genproto/golang"
)

//HashValue ...
func HashValue(text *string, location message_types.Location) error {

	pos := location.NewStart + location.Length
	if int32(len(*text)) < pos {
		return errors.New("Indexes for values: are out of bounds")
	}
	runeText := []rune(*text)

	before := runeText[:location.NewStart]
	after := runeText[pos:]
	curValue := string(runeText[location.NewStart:pos])
	concat := string(before) + hash(curValue) + string(after)
	runeText = []rune(concat)
	*text = string(runeText)
	return nil
}

func hash(s string) string {
	h := fnv.New32a()
	h.Write([]byte(s))
	result := h.Sum32()
	return fmt.Sprint(result)
}
