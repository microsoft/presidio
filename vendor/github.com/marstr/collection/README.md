# collection
[![GoDoc](https://godoc.org/github.com/marstr/collection?status.svg)](https://godoc.org/github.com/marstr/collection) [![Build Status](https://travis-ci.org/marstr/collection.svg?branch=master)](https://travis-ci.org/marstr/collection) [![Go Report Card](https://goreportcard.com/badge/github.com/marstr/collection)](https://goreportcard.com/report/github.com/marstr/collection)

# Usage

## Querying Collections
Inspired by .NET's Linq, querying data structures used in this library is a snap! Build Go pipelines quickly and easily which will apply lambdas as they query your data structures.

### Slices
Converting between slices and a queryable structure is as trivial as it should be.
``` Go
original := []interface{}{"a", "b", "c"}
subject := collection.AsEnumerable(original...)

for entry := range subject.Enumerate(nil) {
    fmt.Println(entry)
}
// Output:
// a
// b
// c

```

### Where
``` Go
subject := collection.AsEnumerable(1, 2, 3, 4, 5, 6)
filtered := collection.Where(subject, func(num interface{}) bool{
    return num.(int) > 3
})
for entry := range filtered.Enumerate(nil) {
    fmt.Println(entry)
}
// Output:
// 4
// 5
// 6
```
### Select
``` Go
subject := collection.AsEnumerable(1, 2, 3, 4, 5, 6)
updated := collection.Select(subject, func(num interface{}) interface{}{
    return num.(int) + 10
})
for entry := range updated.Enumerate(nil) {
    fmt.Println(entry)
}
// Output:
// 11
// 12
// 13
// 14
// 15
// 16
```

## Queues
### Creating a Queue

``` Go
done := make(chan struct{})
subject := collection.NewQueue(1, 2, 3, 5, 8, 13, 21)
selected := subject.Enumerate(done).Skip(3).Take(3)
for entry := range selected {
	fmt.Println(entry)
}
close(done)
// Output:
// 5
// 8
// 13
```

### Checking if a Queue is empty
``` Go
populated := collection.NewQueue(1, 2, 3, 5, 8, 13)
notPopulated := collection.NewQueue()
fmt.Println(populated.IsEmpty())
fmt.Println(notPopulated.IsEmpty())
// Output:
// false
// true
```

# Versioning
This library will conform to strict semantic versions as defined by [semver.org](http://semver.org/spec/v2.0.0.html)'s v2 specification.

# Contributing
I accept contributions! To ensure `glide` users and `go get` users retrieve the same commit, please submit PRs to the 'dev' branch. Remember to add tests!
