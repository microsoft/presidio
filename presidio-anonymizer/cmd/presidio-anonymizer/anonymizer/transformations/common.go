package transformations

import "fmt"

func replaceValueInString(original string, new string, before int, after int) string {
	t := []rune(original)
	b := t[:before]
	a := t[after:]
	return fmt.Sprintf("%s%s%s", string(b), new, string(a))
}
