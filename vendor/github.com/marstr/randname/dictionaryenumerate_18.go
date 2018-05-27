// +build go1.8

package randname

import (
	"sort"

	"github.com/marstr/collection"
)

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

		alphabetizedChildren := []rune{}
		for letter := range subject.Children {
			alphabetizedChildren = append(alphabetizedChildren, letter)
		}
		sort.Slice(alphabetizedChildren, func(i, j int) bool {
			return alphabetizedChildren[i] < alphabetizedChildren[j]
		})

		for _, letter := range alphabetizedChildren {
			enumerateHelper(*subject.Children[letter], prefix+string(letter))
		}
	}

	go func() {
		defer close(results)
		enumerateHelper(node, "")
	}()

	return results
}
