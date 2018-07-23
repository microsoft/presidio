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
		NewStart: 10,
		End:      14,
		Length:   4,
	}
	index1 := message_types.Location{
		NewStart: 27,
		End:      31,
		Length:   4,
	}
	locations[0] = index0
	locations[1] = index1
	err := HashValue(&str, locations[0])
	if err != nil {
		assert.Error(t, err)
	}

	err = HashValue(&str, locations[1])
	if err != nil {
		assert.Error(t, err)
	}

	expected := "this is a 425748966156 and 40419098051"

	assert.Equal(t, expected, str)
}
