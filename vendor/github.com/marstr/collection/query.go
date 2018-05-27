package collection

import (
	"errors"
	"reflect"
	"runtime"
	"sync"
)

// Enumerable offers a means of easily converting into a channel. It is most
// useful for types where mutability is not in question.
type Enumerable interface {
	Enumerate(cancel <-chan struct{}) Enumerator
}

// Enumerator exposes a new syntax for querying familiar data structures.
type Enumerator <-chan interface{}

// Predicate defines an interface for funcs that make some logical test.
type Predicate func(interface{}) bool

// Transform defines a function which takes a value, and returns some value based on the original.
type Transform func(interface{}) interface{}

// Unfolder defines a function which takes a single value, and exposes many of them as an Enumerator
type Unfolder func(interface{}) Enumerator

type emptyEnumerable struct{}

var (
	errNoElements       = errors.New("Enumerator encountered no elements")
	errMultipleElements = errors.New("Enumerator encountered multiple elements")
)

// IsErrorNoElements determines whethr or not the given error is the result of no values being
// returned when one or more were expected.
func IsErrorNoElements(err error) bool {
	return err == errNoElements
}

// IsErrorMultipleElements determines whether or not the given error is the result of multiple values
// being returned when one or zero were expected.
func IsErrorMultipleElements(err error) bool {
	return err == errMultipleElements
}

// Identity is a trivial Transform which applies no operation on the value.
var Identity Transform = func(value interface{}) interface{} {
	return value
}

// Empty is an Enumerable that has no elements, and will never have any elements.
var Empty Enumerable = &emptyEnumerable{}

func (e emptyEnumerable) Enumerate(cancel <-chan struct{}) Enumerator {
	results := make(chan interface{})
	close(results)
	return results
}

// All tests whether or not all items present in an Enumerable meet a criteria.
func All(subject Enumerable, p Predicate) bool {
	done := make(chan struct{})
	defer close(done)

	return subject.Enumerate(done).All(p)
}

// All tests whether or not all items present meet a criteria.
func (iter Enumerator) All(p Predicate) bool {
	for entry := range iter {
		if !p(entry) {
			return false
		}
	}
	return true
}

// Any tests an Enumerable to see if there are any elements present.
func Any(iterator Enumerable) bool {
	done := make(chan struct{})
	defer close(done)

	for range iterator.Enumerate(done) {
		return true
	}
	return false
}

// Anyp tests an Enumerable to see if there are any elements present that meet a criteria.
func Anyp(iterator Enumerable, p Predicate) bool {
	done := make(chan struct{})
	defer close(done)

	for element := range iterator.Enumerate(done) {
		if p(element) {
			return true
		}
	}
	return false
}

type enumerableSlice []interface{}

func (f enumerableSlice) Enumerate(cancel <-chan struct{}) Enumerator {
	results := make(chan interface{})

	go func() {
		defer close(results)
		for _, entry := range f {
			select {
			case results <- entry:
				break
			case <-cancel:
				return
			}
		}
	}()

	return results
}

type enumerableValue struct {
	reflect.Value
}

func (v enumerableValue) Enumerate(cancel <-chan struct{}) Enumerator {
	results := make(chan interface{})

	go func() {
		defer close(results)

		elements := v.Len()

		for i := 0; i < elements; i++ {
			select {
			case results <- v.Index(i).Interface():
				break
			case <-cancel:
				return
			}
		}
	}()

	return results
}

// AsEnumerable allows for easy conversion of a slice to a re-usable Enumerable object.
func AsEnumerable(entries ...interface{}) Enumerable {
	if len(entries) != 1 {
		return enumerableSlice(entries)
	}

	val := reflect.ValueOf(entries[0])

	if kind := val.Kind(); kind == reflect.Slice || kind == reflect.Array {
		return enumerableValue{
			Value: val,
		}
	}
	return enumerableSlice(entries)
}

// AsEnumerable stores the results of an Enumerator so the results can be enumerated over repeatedly.
func (iter Enumerator) AsEnumerable() Enumerable {
	return enumerableSlice(iter.ToSlice())
}

// Count iterates over a list and keeps a running tally of the number of elements
// satisfy a predicate.
func Count(iter Enumerable, p Predicate) int {
	return iter.Enumerate(nil).Count(p)
}

// Count iterates over a list and keeps a running tally of the number of elements
// satisfy a predicate.
func (iter Enumerator) Count(p Predicate) int {
	tally := 0
	for entry := range iter {
		if p(entry) {
			tally++
		}
	}
	return tally
}

// CountAll iterates over a list and keeps a running tally of how many it's seen.
func CountAll(iter Enumerable) int {
	return iter.Enumerate(nil).CountAll()
}

// CountAll iterates over a list and keeps a running tally of how many it's seen.
func (iter Enumerator) CountAll() int {
	tally := 0
	for range iter {
		tally++
	}
	return tally
}

// Discard reads an enumerator to the end but does nothing with it.
// This method should be used in circumstances when it doesn't make sense to explicitly cancel the Enumeration.
func (iter Enumerator) Discard() {
	for range iter {
		// Intentionally Left Blank
	}
}

// ElementAt retreives an item at a particular position in an Enumerator.
func ElementAt(iter Enumerable, n uint) interface{} {
	done := make(chan struct{})
	defer close(done)
	return iter.Enumerate(done).ElementAt(n)
}

// ElementAt retreives an item at a particular position in an Enumerator.
func (iter Enumerator) ElementAt(n uint) interface{} {
	for i := uint(0); i < n; i++ {
		<-iter
	}
	return <-iter
}

// First retrieves just the first item in the list, or returns an error if there are no elements in the array.
func First(subject Enumerable) (retval interface{}, err error) {
	done := make(chan struct{})

	err = errNoElements

	var isOpen bool

	if retval, isOpen = <-subject.Enumerate(done); isOpen {
		err = nil
	}
	close(done)

	return
}

// Last retreives the item logically behind all other elements in the list.
func Last(iter Enumerable) interface{} {
	return iter.Enumerate(nil).Last()
}

// Last retreives the item logically behind all other elements in the list.
func (iter Enumerator) Last() (retval interface{}) {
	for retval = range iter {
		// Intentionally Left Blank
	}
	return
}

type merger struct {
	originals []Enumerable
}

func (m merger) Enumerate(cancel <-chan struct{}) Enumerator {
	retval := make(chan interface{})

	var wg sync.WaitGroup
	wg.Add(len(m.originals))
	for _, item := range m.originals {
		go func(input Enumerable) {
			defer wg.Done()
			for value := range input.Enumerate(cancel) {
				retval <- value
			}
		}(item)
	}

	go func() {
		wg.Wait()
		close(retval)
	}()
	return retval
}

// Merge takes the results as it receives them from several channels and directs
// them into a single channel.
func Merge(channels ...Enumerable) Enumerable {
	return merger{
		originals: channels,
	}
}

// Merge takes the results of this Enumerator and others, and funnels them into
// a single Enumerator. The order of in which they will be combined is non-deterministic.
func (iter Enumerator) Merge(others ...Enumerator) Enumerator {
	retval := make(chan interface{})

	var wg sync.WaitGroup
	wg.Add(len(others) + 1)

	funnel := func(prevResult Enumerator) {
		for entry := range prevResult {
			retval <- entry
		}
		wg.Done()
	}

	go funnel(iter)
	for _, item := range others {
		go funnel(item)
	}

	go func() {
		wg.Wait()
		close(retval)
	}()
	return retval
}

type parallelSelecter struct {
	original  Enumerable
	operation Transform
}

func (ps parallelSelecter) Enumerate(cancel <-chan struct{}) Enumerator {
	return ps.original.Enumerate(cancel).ParallelSelect(ps.operation)
}

// ParallelSelect creates an Enumerable which will use all logically available CPUs to
// execute a Transform.
func ParallelSelect(original Enumerable, operation Transform) Enumerable {
	return parallelSelecter{
		original:  original,
		operation: operation,
	}
}

// ParallelSelect will execute a Transform across all logical CPUs available to the current process.
func (iter Enumerator) ParallelSelect(operation Transform) Enumerator {
	if cpus := runtime.NumCPU(); cpus != 1 {
		intermediate := iter.splitN(operation, uint(cpus))
		return intermediate[0].Merge(intermediate[1:]...)
	}
	return iter
}

type reverser struct {
	original Enumerable
}

// Reverse will enumerate all values of an enumerable, store them in a Stack, then replay them all.
func Reverse(original Enumerable) Enumerable {
	return reverser{
		original: original,
	}
}

func (r reverser) Enumerate(cancel <-chan struct{}) Enumerator {
	return r.original.Enumerate(cancel).Reverse()
}

// Reverse returns items in the opposite order it encountered them in.
func (iter Enumerator) Reverse() Enumerator {
	cache := NewStack()
	for entry := range iter {
		cache.Push(entry)
	}

	retval := make(chan interface{})

	go func() {
		for !cache.IsEmpty() {
			val, _ := cache.Pop()
			retval <- val
		}
		close(retval)
	}()
	return retval
}

type selecter struct {
	original  Enumerable
	transform Transform
}

func (s selecter) Enumerate(cancel <-chan struct{}) Enumerator {
	return s.original.Enumerate(cancel).Select(s.transform)
}

// Select creates a reusable stream of transformed values.
func Select(subject Enumerable, transform Transform) Enumerable {
	return selecter{
		original:  subject,
		transform: transform,
	}
}

// Select iterates over a list and returns a transformed item.
func (iter Enumerator) Select(transform Transform) Enumerator {
	retval := make(chan interface{})

	go func() {
		for item := range iter {
			retval <- transform(item)
		}
		close(retval)
	}()

	return retval
}

type selectManyer struct {
	original Enumerable
	toMany   Unfolder
}

func (s selectManyer) Enumerate(cancel <-chan struct{}) Enumerator {
	return s.original.Enumerate(cancel).SelectMany(s.toMany)
}

// SelectMany allows for unfolding of values.
func SelectMany(subject Enumerable, toMany Unfolder) Enumerable {
	return selectManyer{
		original: subject,
		toMany:   toMany,
	}
}

// SelectMany allows for flattening of data structures.
func (iter Enumerator) SelectMany(lister Unfolder) Enumerator {
	retval := make(chan interface{})

	go func() {
		for parent := range iter {
			for child := range lister(parent) {
				retval <- child
			}
		}
		close(retval)
	}()

	return retval
}

// Single retreives the only element from a list, or returns nil and an error.
func Single(iter Enumerable) (retval interface{}, err error) {
	done := make(chan struct{})
	defer close(done)

	err = errNoElements

	firstPass := true
	for entry := range iter.Enumerate(done) {
		if firstPass {
			retval = entry
			err = nil
		} else {
			retval = nil
			err = errMultipleElements
			break
		}
		firstPass = false
	}
	return
}

// Singlep retrieces the only element from a list that matches a criteria. If
// no match is found, or two or more are found, `Singlep` returns nil and an
// error.
func Singlep(iter Enumerable, pred Predicate) (retval interface{}, err error) {
	iter = Where(iter, pred)
	return Single(iter)
}

type skipper struct {
	original  Enumerable
	skipCount uint
}

func (s skipper) Enumerate(cancel <-chan struct{}) Enumerator {
	return s.original.Enumerate(cancel).Skip(s.skipCount)
}

// Skip creates a reusable stream which will skip the first `n` elements before iterating
// over the rest of the elements in an Enumerable.
func Skip(subject Enumerable, n uint) Enumerable {
	return skipper{
		original:  subject,
		skipCount: n,
	}
}

// Skip retreives all elements after the first 'n' elements.
func (iter Enumerator) Skip(n uint) Enumerator {
	results := make(chan interface{})

	go func() {
		defer close(results)

		i := uint(0)
		for entry := range iter {
			if i < n {
				i++
				continue
			}
			results <- entry
		}
	}()

	return results
}

// splitN creates N Enumerators, each will be a subset of the original Enumerator and will have
// distinct populations from one another.
func (iter Enumerator) splitN(operation Transform, n uint) []Enumerator {
	results, cast := make([]chan interface{}, n, n), make([]Enumerator, n, n)

	for i := uint(0); i < n; i++ {
		results[i] = make(chan interface{})
		cast[i] = results[i]
	}

	go func() {
		for i := uint(0); i < n; i++ {
			go func(addr uint) {
				defer close(results[addr])
				for {
					read, ok := <-iter
					if !ok {
						return
					}
					results[addr] <- operation(read)
				}
			}(i)
		}
	}()

	return cast
}

type taker struct {
	original Enumerable
	n        uint
}

func (t taker) Enumerate(cancel <-chan struct{}) Enumerator {
	return t.original.Enumerate(cancel).Take(t.n)
}

// Take retreives just the first `n` elements from an Enumerable.
func Take(subject Enumerable, n uint) Enumerable {
	return taker{
		original: subject,
		n:        n,
	}
}

// Take retreives just the first 'n' elements from an Enumerator.
func (iter Enumerator) Take(n uint) Enumerator {
	results := make(chan interface{})

	go func() {
		defer close(results)
		i := uint(0)
		for entry := range iter {
			if i >= n {
				return
			}
			i++
			results <- entry
		}
	}()

	return results
}

type takeWhiler struct {
	original Enumerable
	criteria func(interface{}, uint) bool
}

func (tw takeWhiler) Enumerate(cancel <-chan struct{}) Enumerator {
	return tw.original.Enumerate(cancel).TakeWhile(tw.criteria)
}

// TakeWhile creates a reusable stream which will halt once some criteria is no longer met.
func TakeWhile(subject Enumerable, criteria func(interface{}, uint) bool) Enumerable {
	return takeWhiler{
		original: subject,
		criteria: criteria,
	}
}

// TakeWhile continues returning items as long as 'criteria' holds true.
func (iter Enumerator) TakeWhile(criteria func(interface{}, uint) bool) Enumerator {
	results := make(chan interface{})

	go func() {
		defer close(results)
		i := uint(0)
		for entry := range iter {
			if !criteria(entry, i) {
				return
			}
			i++
			results <- entry
		}
	}()

	return results
}

// Tee creates two Enumerators which will have identical contents as one another.
func (iter Enumerator) Tee() (Enumerator, Enumerator) {
	left, right := make(chan interface{}), make(chan interface{})

	go func() {
		for entry := range iter {
			left <- entry
			right <- entry
		}
		close(left)
		close(right)
	}()

	return left, right
}

// ToSlice places all iterated over values in a Slice for easy consumption.
func ToSlice(iter Enumerable) []interface{} {
	return iter.Enumerate(nil).ToSlice()
}

// ToSlice places all iterated over values in a Slice for easy consumption.
func (iter Enumerator) ToSlice() []interface{} {
	retval := make([]interface{}, 0)
	for entry := range iter {
		retval = append(retval, entry)
	}
	return retval
}

type wherer struct {
	original Enumerable
	filter   Predicate
}

func (w wherer) Enumerate(cancel <-chan struct{}) Enumerator {
	retval := make(chan interface{})

	go func() {
		defer close(retval)
		for entry := range w.original.Enumerate(cancel) {
			if w.filter(entry) {
				retval <- entry
			}
		}
	}()

	return retval
}

// Where creates a reusable means of filtering a stream.
func Where(original Enumerable, p Predicate) Enumerable {
	return wherer{
		original: original,
		filter:   p,
	}
}

// Where iterates over a list and returns only the elements that satisfy a
// predicate.
func (iter Enumerator) Where(predicate Predicate) Enumerator {
	retval := make(chan interface{})
	go func() {
		for item := range iter {
			if predicate(item) {
				retval <- item
			}
		}
		close(retval)
	}()

	return retval
}

// UCount iterates over a list and keeps a running tally of the number of elements
// satisfy a predicate.
func UCount(iter Enumerable, p Predicate) uint {
	return iter.Enumerate(nil).UCount(p)
}

// UCount iterates over a list and keeps a running tally of the number of elements
// satisfy a predicate.
func (iter Enumerator) UCount(p Predicate) uint {
	tally := uint(0)
	for entry := range iter {
		if p(entry) {
			tally++
		}
	}
	return tally
}

// UCountAll iterates over a list and keeps a running tally of how many it's seen.
func UCountAll(iter Enumerable) uint {
	return iter.Enumerate(nil).UCountAll()
}

// UCountAll iterates over a list and keeps a running tally of how many it's seen.
func (iter Enumerator) UCountAll() uint {
	tally := uint(0)
	for range iter {
		tally++
	}
	return tally
}
