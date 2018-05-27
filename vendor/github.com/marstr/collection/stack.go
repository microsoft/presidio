package collection

import (
	"sync"
)

// Stack implements a basic FILO structure.
type Stack struct {
	underlyer *LinkedList
	key       sync.RWMutex
}

// NewStack instantiates a new FILO structure.
func NewStack(entries ...interface{}) *Stack {
	retval := &Stack{}
	retval.underlyer = NewLinkedList()

	for _, entry := range entries {
		retval.Push(entry)
	}
	return retval
}

// Enumerate peeks at each element in the stack without mutating it.
func (stack *Stack) Enumerate(cancel <-chan struct{}) Enumerator {
	stack.key.RLock()
	defer stack.key.RUnlock()

	return stack.underlyer.Enumerate(cancel)
}

// IsEmpty tests the Stack to determine if it is populate or not.
func (stack *Stack) IsEmpty() bool {
	stack.key.RLock()
	defer stack.key.RUnlock()
	return stack.underlyer == nil || stack.underlyer.IsEmpty()
}

// Push adds an entry to the top of the Stack.
func (stack *Stack) Push(entry interface{}) {
	stack.key.Lock()
	defer stack.key.Unlock()

	if nil == stack.underlyer {
		stack.underlyer = NewLinkedList()
	}
	stack.underlyer.AddFront(entry)
}

// Pop returns the entry at the top of the Stack then removes it.
func (stack *Stack) Pop() (interface{}, bool) {
	stack.key.Lock()
	defer stack.key.Unlock()

	if nil == stack.underlyer {
		return nil, false
	}
	return stack.underlyer.RemoveFront()
}

// Peek returns the entry at the top of the Stack without removing it.
func (stack *Stack) Peek() (interface{}, bool) {
	stack.key.RLock()
	defer stack.key.RUnlock()
	return stack.underlyer.PeekFront()
}

// Size returns the number of entries populating the Stack.
func (stack *Stack) Size() uint {
	stack.key.RLock()
	defer stack.key.RUnlock()
	if stack.underlyer == nil {
		return 0
	}
	return stack.underlyer.Length()
}
