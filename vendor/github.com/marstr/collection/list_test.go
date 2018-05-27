package collection

import "fmt"

func ExampleList_AddAt() {
	subject := NewList(0, 1, 4, 5, 6)
	subject.AddAt(2, 2, 3)
	fmt.Println(subject)
	// Output: [0 1 2 3 4 5 6]
}
