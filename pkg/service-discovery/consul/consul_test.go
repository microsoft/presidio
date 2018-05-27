package consul

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestRegister(t *testing.T) {
	const redis = "redis"
	store := New()
	err := store.Register(redis, "localhost", 6379)
	if err != nil {
		t.Fatal(err)
	}
	address, err1 := store.GetService(redis)
	if err1 != nil {
		t.Fatal(err1)
	}

	assert.Equal(t, "localhost:6379", address)

	err2 := store.DeRegister(redis)
	if err2 != nil {
		t.Fatal(err2)
	}
}

func TestDeRegister(t *testing.T) {
	const redis = "redis"
	store := New()
	err := store.Register(redis, "localhost", 6379)
	if err != nil {
		t.Fatal(err)
	}

	err1 := store.DeRegister(redis)
	if err1 != nil {
		t.Fatal(err1)
	}

	_, err2 := store.GetService(redis)

	assert.Error(t, err2, "localhost:6379")

}
