package myName

import (
	"net/http"
)

func Foo(a, b string) int {
	return Bar(a, b)
}

func Bar(c, d string) (retval int) {
	if c == "" {
		retval++
	}

	if d == "" {
		retval++
	}

	return
}


func Baz(x int) string {
	return http.StatusText(x)
}