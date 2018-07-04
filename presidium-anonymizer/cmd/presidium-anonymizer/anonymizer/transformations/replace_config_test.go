package transformations

import (
	"testing"

	"github.com/stretchr/testify/assert"

	message_types "github.com/presidium-io/presidium-genproto/golang"
)

func TestReplaceValueSize1(t *testing.T) {

	var str = "this is a 123456 and 54321"

	var locations = make([]message_types.Location, 2)
	index0 := message_types.Location{
		NewStart: 10,
		End:      16,
		Length:   6,
	}
	index1 := message_types.Location{
		NewStart: 19,
		End:      26,
		Length:   5,
	}
	locations[0] = index0
	locations[1] = index1
	err := ReplaceValue(&str, locations[0], "test")
	if err != nil {
		assert.Error(t, err)
	}

	err = ReplaceValue(&str, locations[1], "test")
	if err != nil {
		assert.Error(t, err)
	}

	expected := "this is a test and test"

	assert.Equal(t, expected, str)
}

func TestReplaceValueSize2(t *testing.T) {

	var str = "this is a 126 and 5431"

	var locations = make([]message_types.Location, 2)
	index0 := message_types.Location{
		NewStart: 10,
		End:      13,
		Length:   3,
	}
	index1 := message_types.Location{
		NewStart: 19,
		End:      22,
		Length:   4,
	}
	locations[0] = index0
	locations[1] = index1
	err := ReplaceValue(&str, locations[0], "test")
	if err != nil {
		assert.Error(t, err)
	}

	err = ReplaceValue(&str, locations[1], "test")
	if err != nil {
		assert.Error(t, err)
	}

	expected := "this is a test and test"

	assert.Equal(t, expected, str)
}

func TestReplaceValueSize3(t *testing.T) {

	var str = "this is a 1263 and 54319"

	var locations = make([]message_types.Location, 2)
	index0 := message_types.Location{
		NewStart: 10,
		End:      14,
		Length:   4,
	}
	index1 := message_types.Location{
		NewStart: 19,
		End:      24,
		Length:   5,
	}
	locations[0] = index0
	locations[1] = index1
	err := ReplaceValue(&str, locations[0], "test")
	if err != nil {
		assert.Error(t, err)
	}
	err = ReplaceValue(&str, locations[1], "test")
	if err != nil {
		assert.Error(t, err)
	}

	expected := "this is a test and test"

	assert.Equal(t, expected, str)
}

func TestReplaceValueSize4(t *testing.T) {

	var str = "this is a 1263 and 5439"

	var locations = make([]message_types.Location, 2)
	index0 := message_types.Location{
		NewStart: 10,
		End:      14,
		Length:   4,
	}
	index1 := message_types.Location{
		NewStart: 19,
		End:      23,
		Length:   4,
	}
	locations[0] = index0
	locations[1] = index1
	err := ReplaceValue(&str, locations[0], "test")
	if err != nil {
		assert.Error(t, err)
	}

	err = ReplaceValue(&str, locations[1], "test")
	if err != nil {
		assert.Error(t, err)
	}

	expected := "this is a test and test"

	assert.Equal(t, expected, str)
}
