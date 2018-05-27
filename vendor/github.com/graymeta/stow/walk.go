package stow

// DEV NOTE: tests for this are in test/test.go

// WalkFunc is a function called for each Item visited
// by Walk.
// If there was a problem, the incoming error will describe
// the problem and the function can decide how to handle
// that error.
// If an error is returned, processing stops.
type WalkFunc func(item Item, err error) error

// Walk walks all Items in the Container.
// Returns the first error returned by the WalkFunc or
// nil if no errors were returned.
// The pageSize is the number of Items to get per request.
func Walk(container Container, prefix string, pageSize int, fn WalkFunc) error {
	var (
		err    error
		items  []Item
		cursor = CursorStart
	)
	for {
		items, cursor, err = container.Items(prefix, cursor, pageSize)
		if err != nil {
			err = fn(nil, err)
			if err != nil {
				return err
			}
		}
		for _, item := range items {
			err = fn(item, nil)
			if err != nil {
				return err
			}
		}
		if IsCursorEnd(cursor) {
			break
		}
	}
	return nil
}

// WalkContainersFunc is a function called for each Container visited
// by WalkContainers.
// If there was a problem, the incoming error will describe
// the problem and the function can decide how to handle
// that error.
// If an error is returned, processing stops.
type WalkContainersFunc func(container Container, err error) error

// WalkContainers walks all Containers in the Location.
// Returns the first error returned by the WalkContainersFunc or
// nil if no errors were returned.
// The pageSize is the number of Containers to get per request.
func WalkContainers(location Location, prefix string, pageSize int, fn WalkContainersFunc) error {
	var (
		err        error
		containers []Container
		cursor     = CursorStart
	)
	for {
		containers, cursor, err = location.Containers(prefix, cursor, pageSize)
		if err != nil {
			err = fn(nil, err)
			if err != nil {
				return err
			}
		}
		for _, container := range containers {
			err = fn(container, nil)
			if err != nil {
				return err
			}
		}
		if IsCursorEnd(cursor) {
			break
		}
	}
	return nil
}
