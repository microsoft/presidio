package transformations

import (
	"crypto/sha256"
	"fmt"
	"strings"

	types "github.com/Microsoft/presidio-genproto/golang"
)

//HashValue ...
func HashValue(text string, location types.Location) (string, error) {
	if location.Length == 0 {
		location.Length = location.End - location.Start
	}
	pos := location.Start + location.Length
	if int32(len(text)) < pos {
		return "", fmt.Errorf("Indexes for values: are out of bounds")
	}

	curValue := strings.ToLower(text[location.Start:pos])

	value, err := hash(curValue)
	if err != nil {
		return "", err
	}

	new := replaceValueInString(text, value, int(location.Start), int(pos))
	return new, nil
}

func hash(s string) (string, error) {
	h := sha256.New()
	_, err := h.Write([]byte(s))
	if err != nil {
		return "", err
	}
	return fmt.Sprintf("%x", h.Sum(nil)), nil
}
