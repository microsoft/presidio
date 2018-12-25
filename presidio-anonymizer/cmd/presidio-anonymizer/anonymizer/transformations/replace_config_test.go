package transformations

import (
	"testing"

	"github.com/stretchr/testify/assert"

	types "github.com/Microsoft/presidio-genproto/golang"
)

func TestReplaceValueSize1(t *testing.T) {

	var str = "this is a 123456 and 54321"

	var locations = make([]types.Location, 2)
	index0 := types.Location{
		Start:  10,
		End:    16,
		Length: 6,
	}
	index1 := types.Location{
		Start:  21,
		End:    26,
		Length: 5,
	}
	locations[0] = index0
	locations[1] = index1
	result, err := ReplaceValue(str, locations[1], "test")
	assert.NoError(t, err)

	result, err = ReplaceValue(result, locations[0], "test")
	assert.NoError(t, err)

	expected := "this is a test and test"

	assert.Equal(t, expected, result)
}

func TestReplaceValueSize2(t *testing.T) {

	var str = "this is a 126 and 5431"

	var locations = make([]types.Location, 2)
	index0 := types.Location{
		Start:  10,
		End:    13,
		Length: 3,
	}
	index1 := types.Location{
		Start:  18,
		End:    21,
		Length: 4,
	}
	locations[0] = index0
	locations[1] = index1
	result, err := ReplaceValue(str, locations[1], "test")
	assert.NoError(t, err)

	result, err = ReplaceValue(result, locations[0], "test")
	assert.NoError(t, err)

	expected := "this is a test and test"

	assert.Equal(t, expected, result)
}

func TestReplaceValueSize3(t *testing.T) {

	var str = "this is a 1263 and 54319"

	var locations = make([]types.Location, 2)
	index0 := types.Location{
		Start:  10,
		End:    14,
		Length: 4,
	}
	index1 := types.Location{
		Start:  19,
		End:    24,
		Length: 5,
	}
	locations[0] = index0
	locations[1] = index1
	result, err := ReplaceValue(str, locations[1], "test")
	assert.NoError(t, err)

	result, err = ReplaceValue(result, locations[0], "test")
	assert.NoError(t, err)

	expected := "this is a test and test"

	assert.Equal(t, expected, result)
}

func TestReplaceValueSize4(t *testing.T) {

	var str = "this is a 1263 and 5439"

	var locations = make([]types.Location, 2)
	index0 := types.Location{
		Start:  10,
		End:    14,
		Length: 4,
	}
	index1 := types.Location{
		Start:  19,
		End:    23,
		Length: 4,
	}
	locations[0] = index0
	locations[1] = index1
	result, err := ReplaceValue(str, locations[1], "test")
	assert.NoError(t, err)

	result, err = ReplaceValue(result, locations[0], "test")
	assert.NoError(t, err)

	expected := "this is a test and test"

	assert.Equal(t, expected, result)
}
