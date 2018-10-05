package transformations

import (
	b64 "encoding/base64"
	"fmt"
	"strings"

	"github.com/capitalone/fpe/ff1"

	types "github.com/Microsoft/presidio-genproto/golang"
)

// max tweak length
const maxTweakLength = 8

// radix/base
const radix = 10

//FFIValue encrypt/decrypt value with FF1 algorithm
func FFIValue(text string, location types.Location, key string, tweak string, isDecrypt bool) (string, error) {

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

	runeText := []rune(strings.ToLower(text))

	before := runeText[:location.Start]
	after := runeText[pos:]
	curValue := string(runeText[location.Start:pos])

	var value string
	if !isDecrypt {
		value, err = encrypt(curValue, k, t)
	} else {
		value, err = decrypt(curValue, k, t)
	}
	if err != nil {
		return "", err
	}
	concat := string(before) + value + string(after)
	runeText = []rune(concat)
	return string(runeText), nil
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
