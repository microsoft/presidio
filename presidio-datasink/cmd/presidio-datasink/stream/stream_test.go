package stream

import (
	"testing"

	"context"

	"github.com/stretchr/testify/assert"

	types "github.com/Microsoft/presidio-genproto/golang"

	"github.com/Microsoft/presidio/pkg/presidio"
	"github.com/Microsoft/presidio/pkg/stream/mock"
)

func TestResultsAreWrittenToStream(t *testing.T) {
	// Setup
	mock := mock.New("test")
	mockStream := streamDatasink{stream: mock}
	path := "partition1/sequence1"
	resultString, _ := presidio.ConvertInterfaceToJSON(&types.DatasinkRequest{
		AnalyzeResults: getAnalyzerMockResult(),
		Path:           path,
	})

	// Act
	mockStream.WriteAnalyzeResults(getAnalyzerMockResult(), path)
	receive := func(ctx context.Context, partition string, seq string, message string) error {
		// verify
		assert.Equal(t, resultString, message)
		assert.Equal(t, "1", partition)
		return nil
	}

	err := mock.Receive(receive)
	if err != nil {
		t.Fatal(err)
	}
}

func getAnalyzerMockResult() []*types.AnalyzeResult {
	return [](*types.AnalyzeResult){
		&types.AnalyzeResult{
			Field: &types.FieldTypes{Name: types.FieldTypesEnum_PHONE_NUMBER.String()},
			Text:  "(555) 253-0000",
			Score: 1.0,
			Location: &types.Location{
				Start: 153, End: 163, Length: 10,
			},
		},
	}
}
