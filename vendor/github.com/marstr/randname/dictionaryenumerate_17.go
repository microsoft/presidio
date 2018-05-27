// +build !go1.8

package randname

import "github.com/marstr/collection"

func (node trieNode) Enumerate(cancel <-chan struct{}) collection.Enumerator {
	var enumerateHelper func(trieNode, string)

	results := make(chan interface{})

	enumerateHelper = func(subject trieNode, prefix string) {
		if subject.IsWord {
			select {
			case results <- prefix:
			case <-cancel:
				return
			}
		}

		for letter, child := range subject.Children {
			enumerateHelper(*child, prefix+string(letter))
		}
	}

	go func() {
		defer close(results)
		enumerateHelper(node, "")
	}()

	return results
}
