package collection

import (
	"testing"
	"time"
)

func Test_Empty(t *testing.T) {
	if Any(Empty) {
		t.Log("empty should not have any elements")
		t.Fail()
	}

	if CountAll(Empty) != 0 {
		t.Log("empty should have counted to zero elements")
		t.Fail()
	}

	alwaysTrue := func(x interface{}) bool {
		return true
	}

	if Count(Empty, alwaysTrue) != 0 {
		t.Log("empty should have counted to zero even when discriminating")
		t.Fail()
	}
}

func BenchmarkEnumerator_Sum(b *testing.B) {
	nums := AsEnumerable(getInitializedSequentialArray()...)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		for range nums.Enumerate(nil).Select(sleepIdentity) {
			// Intentionally Left Blank
		}
	}
}

func sleepIdentity(num interface{}) interface{} {
	time.Sleep(2 * time.Millisecond)
	return Identity(num)
}

func getInitializedSequentialArray() []interface{} {

	rawNums := make([]interface{}, 1000, 1000)
	for i := range rawNums {
		rawNums[i] = i + 1
	}
	return rawNums
}
