package transformations

import (
	"testing"

	"github.com/stretchr/testify/assert"

	message_types "github.com/presid-io/presidio-genproto/golang"
)

func TestHashValue1(t *testing.T) {

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
	result, err := HashValue(str, locations[1])
	if err != nil {
		assert.Error(t, err)
	}

	result, err = HashValue(result, locations[0])
	if err != nil {
		assert.Error(t, err)
	}

	expected := "this is a 2576725674 and 1566801428"

	assert.Equal(t, expected, result)
}
