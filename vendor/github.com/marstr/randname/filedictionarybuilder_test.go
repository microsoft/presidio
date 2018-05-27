package randname

import (
	"path"
	"path/filepath"
	"runtime"
	"testing"
)

func BenchmarkFileDictionaryBuilder_BuildAdjectives(b *testing.B) {
	_, adjFile, _, _ := runtime.Caller(0)
	adjFile = path.Join(filepath.Dir(adjFile), "adjectives.txt")
	recipient := Dictionary{}
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		reader := FileDictionaryBuilder{}
		reader.Build(&recipient)
		b.StopTimer()
		recipient.Clear()
		b.StartTimer()
	}
}

func BenchmarkFileDictionaryBuilder_BuildNouns(b *testing.B) {
	_, nounFile, _, _ := runtime.Caller(0)
	nounFile = path.Join(filepath.Dir(nounFile), "nouns.txt")
	recipient := Dictionary{}
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		reader := FileDictionaryBuilder{}
		reader.Build(&recipient)
		b.StopTimer()
		recipient.Clear()
		b.StartTimer()
	}
}
