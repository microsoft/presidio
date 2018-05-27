package collection

type fibonacciGenerator struct{}

// Fibonacci is an Enumerable which will dynamically generate the fibonacci sequence.
var Fibonacci Enumerable = fibonacciGenerator{}

func (gen fibonacciGenerator) Enumerate(cancel <-chan struct{}) Enumerator {
	retval := make(chan interface{})

	go func() {
		defer close(retval)
		a, b := 0, 1

		for {
			select {
			case retval <- a:
				a, b = b, a+b
			case <-cancel:
				return
			}
		}
	}()

	return retval
}
