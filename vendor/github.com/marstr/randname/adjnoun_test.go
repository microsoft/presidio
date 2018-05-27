// +build go1.7

package randname

import (
	"regexp"
	"testing"
)

var pascalForm = regexp.MustCompile(`^[A-Z][a-z]+[A-Z][a-z]+\d{2}$`)
var camelForm = regexp.MustCompile(`^[a-z]+[A-Z][a-z]+\d{2}$`)

func TestAdjNoun_Generate(t *testing.T) {
	testCases := []struct {
		Format   AdjNounFormat
		Expected *regexp.Regexp
	}{
		{GenerateCamelCaseAdjNoun, camelForm},
		{GeneratePascalCaseAdjNoun, pascalForm},
	}

	subject := AdjNoun{}

	for _, tc := range testCases {
		t.Run("", func(t *testing.T) {
			subject.Format = tc.Format

			result := subject.Generate()
			if !tc.Expected.MatchString(result) {
				t.Fail()
			}
		})
	}
}

func BenchmarkAdjNoun_Generate(b *testing.B) {
	subject := &AdjNoun{}
	subject.Generate() // Prime the pump to separate default Dictionary population time.
	b.ResetTimer()

	for i := 0; i < b.N; i++ {
		subject.Generate()
	}
}
