package randname

import (
	"bytes"
	"crypto/rand"
	"fmt"
	"io"
	"math/big"
	"os"
	"path"
	"path/filepath"
	"runtime"
	"strings"
	"sync"

	"github.com/marstr/collection"
)

// AdjNounFormat is a type of function that aggregates an Adjective, Noun, and Digit into a single formatted string.
type AdjNounFormat func(string, string, int) string

// AdjNoun creates a random name of the form adjectiveNameDigit
type AdjNoun struct {
	Adjectives    *Dictionary
	Format        AdjNounFormat
	Nouns         *Dictionary
	RandGenerator io.Reader
}

// NewAdjNoun creates a new instance of AdjNoun that is populated with all of the defaults.
func NewAdjNoun() *AdjNoun {
	return &AdjNoun{
		RandGenerator: rand.Reader,
		Format:        GeneratePascalCaseAdjNoun,
	}
}

func defaultBuilder(subPath string) func() *Dictionary {
	_, callerFile, _, _ := runtime.Caller(0)

	// try to be as flexible as possible about how folks have included this library and still have default libraries populated.
	searchLocations := []string{
		subPath,
		path.Base(subPath),
		path.Join(filepath.Dir(callerFile), subPath),
	}

	var loader sync.Once
	defaultDictionary := &Dictionary{}
	return func() *Dictionary {
		loader.Do(func() {
			var targetFile string
			for _, loc := range searchLocations {
				if _, err := os.Stat(loc); err == nil {
					targetFile = loc
					break
				}
			}
			reader := FileDictionaryBuilder{
				Target: targetFile,
			}
			reader.Build(defaultDictionary)
		})
		return defaultDictionary
	}
}

var getDefaultAdjectives = defaultBuilder("adjectives.txt")
var getDefaultNouns = defaultBuilder("nouns.txt")

// Generate fetches a random name of the default format and strategy.
func Generate() string {
	return AdjNoun{}.Generate()
}

// Generate creates a new randomly generated name with the
func (adNoun AdjNoun) Generate() string {
	if adNoun.Format == nil {
		adNoun.Format = GeneratePascalCaseAdjNoun
	}
	return adNoun.Format(adNoun.getAdjective(), adNoun.getNoun(), adNoun.getDigit())
}

func (adNoun AdjNoun) getAdjective() string {
	if adNoun.Adjectives == nil {
		adNoun.Adjectives = getDefaultAdjectives()
	}
	if collection.Any(adNoun.Adjectives) {
		if adNoun.RandGenerator == nil {
			adNoun.RandGenerator = rand.Reader
		}
		randomLocation, _ := rand.Int(adNoun.RandGenerator, big.NewInt(adNoun.Adjectives.Size()))
		return collection.ElementAt(adNoun.Adjectives, uint(randomLocation.Uint64())).(string)
	}
	return ""
}

func (adNoun AdjNoun) getNoun() string {
	if adNoun.Nouns == nil {
		adNoun.Nouns = getDefaultNouns()
	}
	if collection.Any(adNoun.Nouns) {
		if adNoun.RandGenerator == nil {
			adNoun.RandGenerator = rand.Reader
		}
		position, _ := rand.Int(adNoun.RandGenerator, big.NewInt(adNoun.Nouns.Size()))
		return collection.ElementAt(adNoun.Nouns, uint(position.Uint64())).(string)
	}
	return ""
}

func (adNoun AdjNoun) getDigit() int {
	if adNoun.RandGenerator == nil {
		adNoun.RandGenerator = rand.Reader
	}
	result, _ := rand.Int(adNoun.RandGenerator, big.NewInt(100))
	return int(result.Int64())
}

// GenerateCamelCaseAdjNoun formats an adjective, noun, and digit in the following way: bigCloud9
func GenerateCamelCaseAdjNoun(adjective, noun string, digit int) string {
	pascal := GeneratePascalCaseAdjNoun(adjective, noun, digit)
	return strings.ToLower(pascal[:1]) + pascal[1:]
}

// GeneratePascalCaseAdjNoun formats an adjective, noun, and digit in the following way: BigCloud9
func GeneratePascalCaseAdjNoun(adjective, noun string, digit int) string {
	builder := bytes.Buffer{}
	if len(adjective) > 0 {
		builder.WriteString(strings.ToUpper(adjective[:1]))
		builder.WriteString(strings.ToLower(adjective[1:]))
	}

	if len(noun) > 0 {
		builder.WriteString(strings.ToUpper(noun[:1]))
		builder.WriteString(strings.ToLower(noun[1:]))
	}

	builder.WriteString(fmt.Sprintf("%02d", digit))

	return builder.String()
}

// GenerateHyphenedAdjNoun formats an adjective, noun, and digit in the following way: big-cloud-9
func GenerateHyphenedAdjNoun(adjective, noun string, digit int) string {
	builder := bytes.Buffer{}
	if len(adjective) > 0 {
		builder.WriteString(strings.ToLower(adjective))
	}
	builder.WriteRune('-')
	if len(adjective) > 0 {
		builder.WriteString(strings.ToLower(noun))
	}
	builder.WriteRune('-')
	builder.WriteString(fmt.Sprintf("%02d", digit))

	return builder.String()
}
