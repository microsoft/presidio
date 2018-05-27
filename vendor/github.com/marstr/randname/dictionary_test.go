// +build go1.7

package randname

import (
	"fmt"
	"regexp"
	"runtime"
	"strings"
	"testing"

	"github.com/marstr/collection"
)

func ExampleDictionary_Add() {
	subject := &Dictionary{}

	const example = "hello"
	fmt.Println(subject.Contains(example))
	fmt.Println(subject.Size())
	subject.Add(example)
	fmt.Println(subject.Contains(example))
	fmt.Println(subject.Size())
	// Output:
	// false
	// 0
	// true
	// 1
}

func ExampleDictionary_Clear() {
	subject := &Dictionary{}

	subject.Add("hello")
	subject.Add("world")

	fmt.Println(subject.Size())
	fmt.Println(collection.CountAll(subject))

	subject.Clear()

	fmt.Println(subject.Size())
	fmt.Println(collection.Any(subject))

	// Output:
	// 2
	// 2
	// 0
	// false
}

func ExampleDictionary_Enumerate() {
	subject := Dictionary{}
	subject.Add("hello")

	upperCase := collection.Select(subject, func(x interface{}) interface{} {
		return strings.ToUpper(x.(string))
	})

	for word := range subject.Enumerate(nil) {
		fmt.Println(word)
	}

	for word := range upperCase.Enumerate(nil) {
		fmt.Println(word)
	}
	// Output:
	// hello
	// HELLO
}

func ExampleDictionary_Remove() {
	const world = "world"
	subject := Dictionary{}
	subject.Add("hello")
	subject.Add(world)

	fmt.Println(subject.Size())
	fmt.Println(collection.CountAll(subject))

	subject.Remove(world)

	fmt.Println(subject.Size())
	fmt.Println(collection.CountAll(subject))
	fmt.Println(collection.Any(subject))

	// Output:
	// 2
	// 2
	// 1
	// 1
	// true
}

func TestDictionary_Enumerate(t *testing.T) {

	gover := runtime.Version()
	verPattern := regexp.MustCompile(`go(?P<major>\d)+\.(?P<minor>\d+)`)

	verMatch := verPattern.FindStringSubmatch(gover)

	var expectAlphabetized bool
	var major, minor int

	if len(verMatch) > 2 {
		fmt.Sscan(verMatch[1], &major)
		fmt.Sscan(verMatch[2], &minor)

		if major >= 1 && minor >= 8 {
			expectAlphabetized = true
		}
	}

	if expectAlphabetized {
		t.Logf("Detected Go Version: %s, keeping alphabetization check.", gover)
	} else {
		t.Logf("Detected Go Version: %s, turning off alphabetization check.", gover)
	}

	dictSets := [][]string{
		{"alpha", "beta", "charlie"},
		{"also", "always"},
		{"canned", "beans"},
		{"duplicated", "duplicated", "after"},
	}

	for _, ds := range dictSets {
		t.Run("", func(t *testing.T) {
			subject := Dictionary{}
			expected := make(map[string]bool)
			added := 0
			for _, entry := range ds {
				if subject.Add(entry) {
					added++
				}
				expected[entry] = false
			}

			expectedSize := len(expected)

			if added != expectedSize {
				t.Logf("`Add` returned true %d times, expected %d times", added, expectedSize)
				t.Fail()
			}

			if subjectSize := collection.CountAll(subject); subjectSize != expectedSize {
				t.Logf("`collection.CountAll` returned %d elements, expected %d", subjectSize, expectedSize)
				t.Fail()
			}

			prev := ""
			for result := range subject.Enumerate(nil) {
				t.Logf(result.(string))
				if alreadySeen, ok := expected[result.(string)]; !ok {
					t.Logf("An unadded value was returned")
					t.Fail()
				} else if alreadySeen {
					t.Logf("\"%s\" was duplicated", result.(string))
					t.Fail()
				}

				if expectAlphabetized && stringle(result.(string), prev) {
					t.Logf("Results \"%s\" and \"%s\" were not alphabetized.", prev, result.(string))
					t.Fail()
				}
				prev = result.(string)

				expected[result.(string)] = true
			}
		})
	}
}

func TestDictionary_Add(t *testing.T) {
	subject := Dictionary{}

	subject.Add("word")

	if rootChildrenCount := len(subject.root.Children); rootChildrenCount != 1 {
		t.Logf("The root should only have one child, got %d instead.", rootChildrenCount)
		t.Fail()
	}

	if retreived, ok := subject.root.Children['w']; ok {
		leaf := retreived.Navigate("ord")
		if leaf == nil {
			t.Log("Unable to navigate from `w`")
			t.Fail()
		} else if !leaf.IsWord {
			t.Log("leaf shoud have been a word")
			t.Fail()
		}
	} else {
		t.Log("Root doesn't have child for `w`")
		t.Fail()
	}
}

func TestTrieNode_Navigate(t *testing.T) {
	leaf := trieNode{
		IsWord: true,
	}
	subject := trieNode{
		Children: map[rune]*trieNode{
			'a': &trieNode{
				Children: map[rune]*trieNode{
					'b': &trieNode{
						Children: map[rune]*trieNode{
							'c': &leaf,
						},
					},
				},
			},
		},
	}

	testCases := []struct {
		address  string
		expected *trieNode
	}{
		{"abc", &leaf},
		{"abd", nil},
		{"", &subject},
		{"a", subject.Children['a']},
	}

	for _, tc := range testCases {
		t.Run("", func(t *testing.T) {
			if result := subject.Navigate(tc.address); result != tc.expected {
				t.Logf("got: %v want: %v", result, tc.expected)
				t.Fail()
			}
		})
	}
}

func Test_stringle(t *testing.T) {
	testCases := []struct {
		left     string
		right    string
		expected bool
	}{
		{"a", "b", true},
		{"b", "a", false},
		{"a", "a", true},
		{"alpha", "b", true},
		{"a", "beta", true},
		{"alpha", "alpha", true},
		{"alpha", "alphabet", true},
		{"alphabet", "alpha", false},
		{"", "a", true},
		{"", "", true},
	}

	for _, tc := range testCases {
		t.Run(strings.Join([]string{tc.left, tc.right}, ","), func(t *testing.T) {
			if got := stringle(tc.left, tc.right); got != tc.expected {
				t.Logf("got: %v want: %v", got, tc.expected)
				t.Fail()
			}
		})
	}
}

func stringle(left, right string) bool {
	other := []byte(right)
	for i, letter := range []byte(left) {
		if i >= len(other) {
			return false
		}

		if letter > other[i] {
			return false
		} else if letter < other[i] {
			break
		}
	}
	return true
}
