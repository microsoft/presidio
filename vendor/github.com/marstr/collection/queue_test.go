package collection

import (
	"fmt"
	"testing"
)

func ExampleQueue_Add() {
	subject := &Queue{}
	subject.Add(1)
	subject.Add(2)
	res, _ := subject.Peek()
	fmt.Println(res)
	// Output: 1
}

func ExampleNewQueue() {
	empty := NewQueue()
	fmt.Println(empty.Length())

	populated := NewQueue(1, 2, 3, 5, 8, 13)
	fmt.Println(populated.Length())
	// Output:
	// 0
	// 6
}

func ExampleQueue_IsEmpty() {
	empty := NewQueue()
	fmt.Println(empty.IsEmpty())

	populated := NewQueue(1, 2, 3, 5, 8, 13)
	fmt.Println(populated.IsEmpty())
	// Output:
	// true
	// false
}

func ExampleQueue_Next() {
	subject := NewQueue(1, 2, 3, 5, 8, 13)
	for !subject.IsEmpty() {
		val, _ := subject.Next()
		fmt.Println(val)
	}
	// Output:
	// 1
	// 2
	// 3
	// 5
	// 8
	// 13
}

func TestQueue_Length(t *testing.T) {
	empty := NewQueue()
	if count := empty.Length(); count != 0 {
		t.Logf("got: %d\nwant: %d", count, 0)
		t.Fail()
	}

	// Not the type magic number you're thinking of!
	// https://en.wikipedia.org/wiki/1729_(number)
	single := NewQueue(1729)
	if count := single.Length(); count != 1 {
		t.Logf("got: %d\nwant: %d", count, 1)
		t.Fail()
	}

	expectedMany := []interface{}{'a', 'b', 'c', 'd', 'e', 'e', 'f', 'g'}
	many := NewQueue(expectedMany...)
	if count := many.Length(); count != uint(len(expectedMany)) {
		t.Logf("got: %d\nwant: %d", count, len(expectedMany))
	}
}

func TestQueue_Length_NonConstructed(t *testing.T) {
	subject := &Queue{}
	if got := subject.Length(); got != 0 {
		t.Logf("got: %d\nwant: %d", got, 0)
		t.Fail()
	}
}

func TestQueue_Next_NonConstructed(t *testing.T) {
	subject := &Queue{}
	if got, ok := subject.Next(); ok {
		t.Logf("Next should not have been ok")
		t.Fail()
	} else if got != nil {
		t.Logf("got: %v\nwant: %v", got, nil)
		t.Fail()
	}
}

func TestQueue_Peek_DoesntRemove(t *testing.T) {
	expected := []interface{}{1, 2, 3}
	subject := NewQueue(expected...)
	if result, ok := subject.Peek(); !ok {
		t.Logf("no item present")
		t.Fail()
	} else if result != expected[0] {
		t.Logf("got: %d\nwant: %d", result, 1)
		t.Fail()
	} else if count := subject.Length(); count != uint(len(expected)) {
		t.Logf("got: %d\nwant: %d", count, len(expected))
	}
}

func TestQueue_Peek_NonConstructed(t *testing.T) {
	subject := &Queue{}
	if got, ok := subject.Peek(); ok {
		t.Logf("Peek should not have been ok")
		t.Fail()
	} else if got != nil {
		t.Logf("got: %v\nwant: %v", got, nil)
		t.Fail()
	}
}

func TestQueue_ToSlice(t *testing.T) {
	subject := NewQueue(0, 1, 1, 2, 3, 5)
	expectedSliceString := "[0 1 1 2 3 5]"
	if result := subject.ToSlice(); len(result) != 6 {
		t.Logf("got: %d\nwant: %d", len(result), 6)
		t.Fail()
	} else if fmt.Sprintf("%v", result) != expectedSliceString {
		t.Logf("got:\n%v\nwant:\n%s\n", result, expectedSliceString)
		t.Fail()
	}
}

func TestQueue_ToSlice_Empty(t *testing.T) {
	subject := NewQueue()
	result := subject.ToSlice()

	if len(result) != 0 {
		t.Logf("result should have been empty")
		t.Fail()
	}
	expectedStr := "[]"
	resultStr := fmt.Sprintf("%v", result)
	if resultStr != expectedStr {
		t.Logf("got:\n%s\nwant:\n%s", resultStr, expectedStr)
		t.Fail()
	}
}

func TestQueue_ToSlice_NotConstructed(t *testing.T) {
	subject := &Queue{}
	result := subject.ToSlice()

	if len(result) != 0 {
		t.Logf("result should have been empty")
		t.Fail()
	}
	expectedStr := "[]"
	resultStr := fmt.Sprintf("%v", result)
	if resultStr != expectedStr {
		t.Logf("got:\n%s\nwant:\n%s", resultStr, expectedStr)
		t.Fail()
	}
}
