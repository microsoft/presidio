package kube

import (
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

func TestPutKVPair(t *testing.T) {

	store, _ := NewFake()

	value := "value1"
	key := "key@key@key"
	err := store.PutKVPair(key, value)
	assert.NoError(t, err)

	time.Sleep(time.Millisecond)

	v1, _ := store.GetKVPair(key)
	if v1 != value {
		t.Fatal("expected value is different")
	}
}

func TestDeleteKVPair(t *testing.T) {
	store, _ := NewFake()

	key := "key@key@key"

	err := store.PutKVPair(key, "somevalue")
	assert.NoError(t, err)

	err = store.DeleteKVPair(key)
	assert.NoError(t, err)

	_, err = store.GetKVPair(key)
	if err == nil {
		t.Fatal("Key wasn't deleted")
	}
}
