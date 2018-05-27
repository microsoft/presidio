package collection

import (
	"fmt"
	"testing"
)

func TestStack_NewStack_FromEmpty(t *testing.T) {
	subject := NewStack()
	subject.Push("alfa")
	subject.Push("bravo")
	subject.Push("charlie")

	if result, ok := subject.Pop(); result != "charlie" || ok != true {
		t.Logf("got: %s %v\nwant: %s %v", result, ok, "charlie", true)
		t.Fail()
	}
	if result, ok := subject.Pop(); result != "bravo" || ok != true {
		t.Logf("got: %s %v\nwant: %s %v", result, ok, "bravo", true)
		t.Fail()
	}
	if result, ok := subject.Pop(); result != "alfa" || ok != true {
		t.Logf("got: %s %v\nwant: %s %v", result, ok, "alfa", true)
		t.Fail()
	}
	if !subject.IsEmpty() {
		t.Log("subject should have been empty.")
		t.Fail()
	}
}

func ExampleNewStack() {
	subject := NewStack(1, 2, 3)
	for !subject.IsEmpty() {
		val, _ := subject.Pop()
		fmt.Println(val)
	}
	// Output:
	// 3
	// 2
	// 1
}

func TestStack_Push_NonConstructor(t *testing.T) {
	subject := &Stack{}

	sizeAssertion := func(want uint) {
		if got := subject.Size(); got != want {
			t.Logf("got: %d\nwant:%d\n", got, want)
			t.Fail()
		}
	}

	sizeAssertion(0)
	subject.Push(1)
	sizeAssertion(1)
	subject.Push(2)
	sizeAssertion(2)

	if result, ok := subject.Pop(); !ok {
		t.Logf("Pop is not ok")
		t.Fail()
	} else if result != 2 {
		t.Logf("got: %d\nwant: %d", result, 2)
		t.Fail()
	}
}

func TestStack_Pop_NonConstructorEmpty(t *testing.T) {
	subject := &Stack{}

	if result, ok := subject.Pop(); ok {
		t.Logf("Pop should not have been okay")
		t.Fail()
	} else if result != nil {
		t.Logf("got: %v\nwant: %v", result, nil)
	}
}
