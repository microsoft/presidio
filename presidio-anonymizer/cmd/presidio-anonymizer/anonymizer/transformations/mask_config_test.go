package transformations

import (
	"testing"

	"github.com/stretchr/testify/assert"

	message_types "github.com/Microsoft/presidio-genproto/golang"
)

func TestMaskValue1(t *testing.T) {

	var str = "this is a 123456 and 54321"

	var locations = make([]message_types.Location, 2)
	index0 := message_types.Location{
		Start:  10,
		End:    14,
		Length: 6,
	}
	index1 := message_types.Location{
		Start:  21,
		End:    26,
		Length: 5,
	}
	locations[0] = index0
	locations[1] = index1
	result, err := MaskValue(str, locations[1], "*", 3, true)
	if err != nil {
		assert.Error(t, err)
	}

	result, err = MaskValue(result, locations[0], "#", 3, false)
	if err != nil {
		assert.Error(t, err)
	}

	expected := "this is a ###456 and 54***"

	assert.Equal(t, expected, result)
}

func TestMaskValue2(t *testing.T) {

	var str = "this is a 123456"

	var locations = make([]message_types.Location, 2)
	index0 := message_types.Location{
		Start:  10,
		End:    14,
		Length: 6,
	}
	locations[0] = index0
	_, err := MaskValue(str, locations[0], "##", 3, false)
	assert.Error(t, err, "Replace Char should be single")
}
