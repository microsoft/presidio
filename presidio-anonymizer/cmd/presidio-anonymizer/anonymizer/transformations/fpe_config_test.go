package transformations

import (
	b64 "encoding/base64"
	"testing"

	"github.com/stretchr/testify/assert"

	types "github.com/Microsoft/presidio-genproto/golang"
)

func TestFFIValue(t *testing.T) {

	var original = "this is a 123-456 and Seattle"

	var locations = make([]types.Location, 2)
	index0 := types.Location{
		Start: 10,
		End:   17,
	}
	index1 := types.Location{
		Start: 22,
		End:   29,
	}
	locations[0] = index0
	locations[1] = index1

	aes128key := []byte{0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f}

	k := b64.StdEncoding.EncodeToString(aes128key)
	tw := b64.StdEncoding.EncodeToString([]byte(""))

	// Encrypt
	result, err := FPEValue(original, locations[1], k, tw, false)
	assert.NoError(t, err)

	result, err = FPEValue(result, locations[0], k, tw, false)
	assert.NoError(t, err)

	expected := "this is a b11-0uU and hPCdL8u"

	assert.Equal(t, expected, result)

	// Descrypt
	result, err = FPEValue(expected, locations[1], k, tw, true)
	assert.NoError(t, err)

	result, err = FPEValue(result, locations[0], k, tw, true)
	assert.NoError(t, err)

	assert.Equal(t, original, result)

}

func TestErrorValue(t *testing.T) {
	var original = "this is a 123456 and 54321"

	var locations = make([]types.Location, 1)
	index0 := types.Location{
		Start:  10,
		End:    14,
		Length: 6,
	}

	locations[0] = index0

	aes128key := []byte{0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f}
	k := b64.StdEncoding.EncodeToString(aes128key)

	// Test tweak size above 8
	tw := b64.StdEncoding.EncodeToString([]byte("123456789"))

	_, err := FPEValue(original, locations[0], k, tw, false)
	assert.Error(t, err)

	// Test invalid key size (key size must be 128, 192 or 256)
	aes128key = []byte{0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e}
	k = b64.StdEncoding.EncodeToString(aes128key)
	tw = b64.StdEncoding.EncodeToString([]byte("12345678"))

	_, err = FPEValue(original, locations[0], k, tw, false)
	assert.Error(t, err)

}
