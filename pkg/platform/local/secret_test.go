package local

import (
	"os"
	"testing"
	"time"
)

func TestPutKVPair(t *testing.T) {

	store := &store{
		path: os.TempDir(),
	}

	value := "value1"
	key := "key@key@key"
	err := store.PutKVPair(key, value)
	if err != nil {
		t.Fatal(err)
	}

	time.Sleep(time.Millisecond)

	v1, _ := store.GetKVPair(key)
	if v1 != value {
		t.Fatal("expected value is different")
	}
}

func TestDeleteKVPair(t *testing.T) {

	store := &store{
		path: os.TempDir(),
	}

	key := "key@key@key"
	err := store.PutKVPair(key, "somevalue")
	if err != nil {
		t.Fatal(err)
	}
	err = store.DeleteKVPair(key)
	if err != nil {
		t.Fatal(err)
	}
	_, err = store.GetKVPair(key)
	if err == nil {
		t.Fatal("Key wasn't deleted")
	}
}
