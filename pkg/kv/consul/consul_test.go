package consul

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestPutGetKV(t *testing.T) {
	store := New()
	err := store.PutKVPair("key", "value")
	if err != nil {
		t.Fatal(err)
	}
	value, err1 := store.GetKVPair("key")
	if err1 != nil {
		t.Fatal(err1)
	}

	assert.Equal(t, "value", value)
}
func TestDeleteKV(t *testing.T) {
	store := New()

	err := store.PutKVPair("key", "value")
	if err != nil {
		t.Fatal(err)
	}

	err1 := store.DeleteKVPair("key")
	if err1 != nil {
		t.Fatal(err1)
	}
	_, err2 := store.GetKVPair("key")

	assert.Error(t, err2, "KV not found")
}
