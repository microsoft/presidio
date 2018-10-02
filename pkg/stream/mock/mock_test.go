package mock

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestStream(t *testing.T) {
	stream := New("test")
	msg := "testmsg"
	err := stream.Send(msg)
	if err != nil {
		t.Fatal(err)
	}

	receive := func(ctx context.Context, partition string, seq string, message string) error {
		assert.Equal(t, msg, message)
		assert.Equal(t, "1", partition)
		return nil
	}

	err = stream.Receive(receive)
	if err != nil {
		t.Fatal(err)
	}
}
