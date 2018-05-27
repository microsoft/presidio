package collection

import (
	"sync"
)

// Queue implements a basic FIFO structure.
type Queue struct {
	underlyer *LinkedList
	key       sync.RWMutex
}

// NewQueue instantiates a new FIFO structure.
func NewQueue(entries ...interface{}) *Queue {
	retval := &Queue{
		underlyer: NewLinkedList(entries...),
	}
	return retval
}

// Add places an item at the back of the Queue.
func (q *Queue) Add(entry interface{}) {
	q.key.Lock()
	defer q.key.Unlock()
	if nil == q.underlyer {
		q.underlyer = NewLinkedList()
	}
	q.underlyer.AddBack(entry)
}

// Enumerate peeks at each element of this queue without mutating it.
func (q *Queue) Enumerate(cancel <-chan struct{}) Enumerator {
	q.key.RLock()
	defer q.key.RUnlock()
	return q.underlyer.Enumerate(cancel)
}

// IsEmpty tests the Queue to determine if it is populate or not.
func (q *Queue) IsEmpty() bool {
	q.key.RLock()
	defer q.key.RUnlock()
	return q.underlyer == nil || q.underlyer.IsEmpty()
}

// Length returns the number of items in the Queue.
func (q *Queue) Length() uint {
	q.key.RLock()
	defer q.key.RUnlock()
	if nil == q.underlyer {
		return 0
	}
	return q.underlyer.length
}

// Next removes and returns the next item in the Queue.
func (q *Queue) Next() (interface{}, bool) {
	q.key.Lock()
	defer q.key.Unlock()
	if q.underlyer == nil {
		return nil, false
	}
	return q.underlyer.RemoveFront()
}

// Peek returns the next item in the Queue without removing it.
func (q *Queue) Peek() (interface{}, bool) {
	q.key.RLock()
	defer q.key.RUnlock()
	if q.underlyer == nil {
		return nil, false
	}
	return q.underlyer.PeekFront()
}

// ToSlice converts a Queue into a slice.
func (q *Queue) ToSlice() []interface{} {
	q.key.RLock()
	defer q.key.RUnlock()

	if q.underlyer == nil {
		return []interface{}{}
	}
	return q.underlyer.ToSlice()
}
