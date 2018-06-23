package transformations

import (
	b64 "encoding/base64"
	"fmt"
	"regexp"

	"github.com/capitalone/fpe/ff1"

	types "github.com/Microsoft/presidio-genproto/golang"
)

// max tweak length
const maxTweakLength = 8

// radix/base
const radix = 62

var validAlphabet = regexp.MustCompile(`[A-Za-z0-9]+`)

//FPEValue encrypt/decrypt value with FF1 algorithm
func FPEValue(text string, location types.Location, key string, tweak string, isDecrypt bool) (string, error) {

	if location.Length == 0 {
		location.Length = location.End - location.Start
	}
	pos := location.Start + location.Length
	if int32(len(text)) < pos {
		return "", fmt.Errorf("Indexes for values: are out of bounds")
	}

	k, err := b64.StdEncoding.DecodeString(key)
	if err != nil {
		return "", err
	}

	t, err := b64.StdEncoding.DecodeString(tweak)
	if err != nil {
		return "", err
	}

	curValue := text[location.Start:pos]

	validCharsIndices := validAlphabet.FindAllStringIndex(curValue, -1)

	for _, indices := range validCharsIndices {
		validChars := curValue[indices[0]:indices[1]]

		var value string
		if !isDecrypt {
			value, err = encrypt(validChars, k, t)
		} else {
			value, err = decrypt(validChars, k, t)
		}
		if err != nil {
			return "", err
		}

		curValue = replaceValueInString(curValue, value, indices[0], indices[1])
	}

	new := replaceValueInString(text, curValue, int(location.Start), int(pos))
	return new, nil
}

func encrypt(s string, key []byte, tweak []byte) (string, error) {

	// Create a new FF1 cipher "object"
	FF1, err := ff1.NewCipher(radix, maxTweakLength, key, tweak)
	if err != nil {
		return "", err
	}

	// Call the encryption function
	c, err := FF1.Encrypt(s)
	if err != nil {
		return "", err
	}
	return c, nil
}

func decrypt(s string, key []byte, tweak []byte) (string, error) {
	// Create a new FF1 cipher "object"
	FF1, err := ff1.NewCipher(radix, maxTweakLength, key, tweak)
	if err != nil {
		return "", err
	}

	// Call the decryption function
	p, err := FF1.Decrypt(s)
	if err != nil {
		return "", err
	}
	return p, nil
}
