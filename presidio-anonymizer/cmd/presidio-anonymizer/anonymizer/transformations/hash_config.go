package transformations

import (
	"errors"
	"fmt"
	"hash/fnv"

	message_types "github.com/Microsoft/presidio-genproto/golang"
)

//HashValue ...
func HashValue(text string, location message_types.Location) (string, error) {
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
	curValue := string(runeText[location.Start:pos])
	value, err := hash(curValue)
	if err != nil {
		return "", err
	}
	concat := string(before) + value + string(after)
	runeText = []rune(concat)
	return string(runeText), nil
}

func hash(s string) (string, error) {
	h := fnv.New32a()
	_, err := h.Write([]byte(s))
	if err != nil {
		return "", err
	}
	result := h.Sum32()
	return fmt.Sprint(result), nil
}
