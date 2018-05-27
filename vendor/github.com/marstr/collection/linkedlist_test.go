package collection

import "fmt"
import "testing"

func ExampleLinkedList_AddFront() {
	subject := NewLinkedList(2, 3)
	subject.AddFront(1)
	result, _ := subject.PeekFront()
	fmt.Println(result)
	// Output: 1
}

func ExampleLinkedList_AddBack() {
	subject := NewLinkedList(2, 3, 5)
	subject.AddBack(8)
	result, _ := subject.PeekBack()
	fmt.Println(result)
	fmt.Println(subject.Length())
	// Output:
	// 8
	// 4
}

func ExampleLinkedList_Enumerate() {
	subject := NewLinkedList(2, 3, 5, 8)
	results := subject.Enumerate(nil).Select(func(a interface{}) interface{} {
		return -1 * a.(int)
	})
	for entry := range results {
		fmt.Println(entry)
	}
	// Output:
	// -2
	// -3
	// -5
	// -8
}

func ExampleLinkedList_Get() {
	subject := NewLinkedList(2, 3, 5, 8)
	val, _ := subject.Get(2)
	fmt.Println(val)
	// Output: 5
}

func TestLinkedList_Get_OutsideBounds(t *testing.T) {
	subject := NewLinkedList(2, 3, 5, 8, 13, 21)
	result, ok := subject.Get(10)
	if !(result == nil && ok == false) {
		t.Logf("got: %v %v\nwant: %v %v", result, ok, nil, false)
		t.Fail()
	}
}

func ExampleNewLinkedList() {
	subject1 := NewLinkedList('a', 'b', 'c', 'd', 'e')
	fmt.Println(subject1.Length())

	slice := []interface{}{1, 2, 3, 4, 5, 6}
	subject2 := NewLinkedList(slice...)
	fmt.Println(subject2.Length())
	// Output:
	// 5
	// 6
}

func TestLinkedList_findLast_empty(t *testing.T) {
	if result := findLast(nil); result != nil {
		t.Logf("got: %v\nwant: %v", result, nil)
	}
}

func TestLinkedList_merge(t *testing.T) {
	testCases := []struct {
		Left     *LinkedList
		Right    *LinkedList
		Expected []int
		Comp     Comparator
	}{
		{
			NewLinkedList(1, 3, 5),
			NewLinkedList(2, 4),
			[]int{1, 2, 3, 4, 5},
			UncheckedComparatori,
		},
		{
			NewLinkedList(1, 2, 3),
			NewLinkedList(),
			[]int{1, 2, 3},
			UncheckedComparatori,
		},
		{
			NewLinkedList(),
			NewLinkedList(1, 2, 3),
			[]int{1, 2, 3},
			UncheckedComparatori,
		},
		{
			NewLinkedList(),
			NewLinkedList(),
			[]int{},
			UncheckedComparatori,
		},
		{
			NewLinkedList(1),
			NewLinkedList(1),
			[]int{1, 1},
			UncheckedComparatori,
		},
		{
			NewLinkedList(2),
			NewLinkedList(1),
			[]int{1, 2},
			UncheckedComparatori,
		},
		{
			NewLinkedList(3),
			NewLinkedList(),
			[]int{3},
			UncheckedComparatori,
		},
		{
			NewLinkedList(),
			NewLinkedList(10),
			[]int{10},
			UncheckedComparatori,
		},
	}

	for _, tc := range testCases {
		t.Run("", func(t *testing.T) {
			result, err := merge(tc.Left.first, tc.Right.first, tc.Comp)
			if err != nil {
				t.Error(err)
			}

			i := 0
			for cursor := result; cursor != nil; cursor, i = cursor.next, i+1 {
				if cursor.payload != tc.Expected[i] {
					t.Logf("got: %d want: %d", cursor.payload.(int), tc.Expected[i])
					t.Fail()
				}
			}

			if expectedLength := len(tc.Expected); i != expectedLength {
				t.Logf("Unexpected length:\n\tgot: %d\n\twant: %d", i, expectedLength)
				t.Fail()
			}
		})
	}
}

func TestLinkedList_mergeSort_repair(t *testing.T) {
	testCases := []*LinkedList{
		NewLinkedList(1, 2, "str1", 4, 5, 6),
		NewLinkedList(1, 2, 3, "str1", 5, 6),
		NewLinkedList(1, 'a', 3, 4, 5, 6),
		NewLinkedList(1, 2, 3, 4, 5, uint(8)),
		NewLinkedList("alpha", 0),
		NewLinkedList(0, "kappa"),
	}

	for _, tc := range testCases {
		t.Run(tc.String(), func(t *testing.T) {
			originalLength := tc.Length()
			originalElements := tc.Enumerate(nil).ToSlice()
			originalContents := tc.String()

			if err := tc.Sorti(); err != ErrUnexpectedType {
				t.Log("`Sorti() should have thrown ErrUnexpectedType")
				t.Fail()
			}

			t.Logf("Contents:\n\tOriginal:   \t%s\n\tPost Merge: \t%s", originalContents, tc.String())

			if newLength := tc.Length(); newLength != originalLength {
				t.Logf("Length changed. got: %d want: %d", newLength, originalLength)
				t.Fail()
			}

			remaining := tc.Enumerate(nil).ToSlice()

			for _, desired := range originalElements {
				found := false
				for i, got := range remaining {
					if got == desired {
						remaining = append(remaining[:i], remaining[i+1:]...)
						found = true
						break
					}
				}

				if !found {
					t.Logf("couldn't find element: %v", desired)
					t.Fail()
				}
			}
		})
	}
}

func ExampleLinkedList_Sort() {
	// Sorti sorts into ascending order, this example demonstrates sorting
	// into descending order.
	subject := NewLinkedList(2, 4, 3, 5, 7, 7)
	subject.Sort(func(a, b interface{}) (int, error) {
		castA, ok := a.(int)
		if !ok {
			return 0, ErrUnexpectedType
		}
		castB, ok := b.(int)
		if !ok {
			return 0, ErrUnexpectedType
		}

		return castB - castA, nil
	})
	fmt.Println(subject)
	// Output: [7 7 5 4 3 2]
}

func ExampleLinkedList_Sorta() {
	subject := NewLinkedList("charlie", "alfa", "bravo", "delta")
	subject.Sorta()
	for _, entry := range subject.ToSlice() {
		fmt.Println(entry.(string))
	}
	// Output:
	// alfa
	// bravo
	// charlie
	// delta
}

func ExampleLinkedList_Sorti() {
	subject := NewLinkedList(7, 3, 2, 2, 3, 6)
	subject.Sorti()
	fmt.Println(subject)
	// Output: [2 2 3 3 6 7]
}

func TestLinkedList_Sorti(t *testing.T) {
	testCases := []struct {
		*LinkedList
		Expected []int
	}{
		{
			NewLinkedList(),
			[]int{},
		},
		{
			NewLinkedList(1, 2, 3, 4),
			[]int{1, 2, 3, 4},
		},
		{
			NewLinkedList(0, -1, 2, 8, 9),
			[]int{-1, 0, 2, 8, 9},
		},
	}

	for _, tc := range testCases {
		t.Run(tc.String(), func(t *testing.T) {
			if err := tc.Sorti(); err != nil {
				t.Error(err)
			}

			sorted := tc.ToSlice()

			if countSorted, countExpected := len(sorted), len(tc.Expected); countSorted != countExpected {
				t.Logf("got: %d want: %d", countSorted, countExpected)
				t.FailNow()
			}

			for i, entry := range sorted {
				cast, ok := entry.(int)
				if !ok {
					t.Errorf("Element was not an int: %v", entry)
				}

				if cast != tc.Expected[i] {
					t.Logf("got: %d want: %d at: %d", cast, tc.Expected[i], i)
					t.Fail()
				}
			}
		})
	}
}

func TestLinkedList_split_Even(t *testing.T) {
	subject := NewLinkedList(1, 2, 3, 4)

	left, right := split(subject.first)
	if left == nil {
		t.Logf("unexpected nil value for left")
		t.Fail()
	} else if left.payload != 1 {
		t.Logf("got: %d\nwant: %d", left.payload, 1)
		t.Fail()
	}

	if right == nil {
		t.Logf("unexpected nil for right")
		t.Fail()
	} else if right.payload != 3 {
		t.Logf("got: %d\nwant: %d", right.payload, 3)
	}
}

func TestLinkedList_split_Odd(t *testing.T) {
	subject := NewLinkedList(1, 2, 3, 4, 5)

	left, right := split(subject.first)

	if left == nil {
		t.Logf("unexpected nil value for left")
		t.Fail()
	} else if left.payload != 1 {
		t.Logf("got: %d\n want: %d", left.payload, 1)
		t.Fail()
	} else if last := findLast(left).payload; last != 2 {
		t.Logf("got:\n%d\nwant:\n%d", last, 2)
		t.Fail()
	}

	if right == nil {
		t.Logf("unexpected nil value for right")
		t.Fail()
	} else if right.payload != 3 {
		t.Logf("got:\n%d\nwant:\n%d", right.payload, 3)
		t.Fail()
	} else if last := findLast(right).payload; last != 5 {
		t.Logf("got:\n%d\nwant:%d", last, 5)
	}
}

func TestLinkedList_split_Empty(t *testing.T) {
	subject := NewLinkedList()

	left, right := split(subject.first)

	if left != nil {
		t.Logf("got: %v\nwant: %v", left, nil)
		t.Fail()
	}

	if right != nil {
		t.Logf("got: %v\nwant: %v", right, nil)
		t.Fail()
	}
}

func TestLinkedList_split_Single(t *testing.T) {
	subject := NewLinkedList(1)

	left, right := split(subject.first)

	if left == nil {
		t.Logf("unexpected nil value for left")
		t.Fail()
	} else if left.payload != 1 {
		t.Logf("got: %d\nwant: %d", left.payload, 1)
		t.Fail()
	}

	if right != nil {
		t.Logf("got: %v\nwant: %v", right, nil)
		t.Fail()
	}

	if last := findLast(left).payload; last != 1 {
		t.Logf("got:\n%d\nwant:\n%d", last, 1)
		t.Fail()
	}
}

func TestLinkedList_split_Double(t *testing.T) {
	subject := NewLinkedList(1, 2)
	left, right := split(subject.first)

	if left == nil {
		t.Logf("unexpected nil value for left")
		t.Fail()
	} else if left.payload != 1 {
		t.Logf("got: %d\nwant: %d", left.payload, 1)
	}

	if right == nil {
		t.Logf("unexpected nil value for right")
		t.Fail()
	} else if right.payload != 2 {
		t.Logf("got: %d\nwant: %d", right.payload, 2)
	}
}

func UncheckedComparatori(a, b interface{}) (int, error) {
	return a.(int) - b.(int), nil
}

func ExampleLinkedList_String() {
	subject1 := NewLinkedList()
	for i := 0; i < 20; i++ {
		subject1.AddBack(i)
	}
	fmt.Println(subject1)

	subject2 := NewLinkedList(1, 2, 3)
	fmt.Println(subject2)
	// Output:
	// [0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 ...]
	// [1 2 3]
}

func ExampleLinkedList_Swap() {
	subject := NewLinkedList(2, 3, 5, 8, 13)
	subject.Swap(1, 3)
	fmt.Println(subject)
	// Output: [2 8 5 3 13]
}

func TestLinkedList_Swap_OutOfBounds(t *testing.T) {
	subject := NewLinkedList(2, 3)
	if err := subject.Swap(0, 8); err == nil {
		t.Log("swap should have failed on y")
		t.Fail()
	}

	if err := subject.Swap(11, 1); err == nil {
		t.Logf("swap shoud have failed on x")
		t.Fail()
	}

	if count := subject.Length(); count != 2 {
		t.Logf("got: %d\nwant: %d", count, 2)
		t.Fail()
	}

	wantStr := "[2 3]"
	gotStr := subject.String()
	if wantStr != gotStr {
		t.Logf("got: %s\nwant: %s", gotStr, wantStr)
		t.Fail()
	}
}
