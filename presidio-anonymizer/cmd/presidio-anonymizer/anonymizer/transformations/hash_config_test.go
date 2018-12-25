package transformations

import (
	"testing"

	"github.com/stretchr/testify/assert"

	types "github.com/Microsoft/presidio-genproto/golang"
)

func TestHashValue1(t *testing.T) {

	var str = "this is a 123456 and 54321"

	var locations = make([]types.Location, 2)
	index0 := types.Location{
		Start:  10,
		End:    14,
		Length: 6,
	}
	index1 := types.Location{
		Start:  21,
		End:    26,
		Length: 5,
	}
	locations[0] = index0
	locations[1] = index1
	result, err := HashValue(str, locations[1])
	assert.NoError(t, err)

	result, err = HashValue(result, locations[0])
	assert.NoError(t, err)

	expected := "this is a 8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92 and 20f3765880a5c269b747e1e906054a4b4a3a991259f1e16b5dde4742cec2319a"

	assert.Equal(t, expected, result)
}
