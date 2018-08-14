package stream

import (
	"testing"

	"github.com/stretchr/testify/assert"

	message_types "github.com/Microsoft/presidio-genproto/golang"
	"github.com/Microsoft/presidio/pkg/stream/mock"
	"github.com/Microsoft/presidio/pkg/templates"
)

func TestResultsAreWrittenToStream(t *testing.T) {
	// Setup
	mock := mock.New("test")
	mockStream := streamDatasink{stream: mock}
	path := "partition1/sequence1"
	resultString, _ := templates.ConvertInterfaceToJSON(&message_types.DatasinkRequest{
		AnalyzeResults: getAnalyzerMockResult(),
		Path:           path,
	})

	// Act
	mockStream.WriteAnalyzeResults(getAnalyzerMockResult(), path)
	receive := func(partition string, seq string, message string) error {
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

func getAnalyzerMockResult() []*message_types.AnalyzeResult {
	return [](*message_types.AnalyzeResult){
		&message_types.AnalyzeResult{
			Field:       &message_types.FieldTypes{Name: message_types.FieldTypesEnum_PHONE_NUMBER.String()},
			Text:        "(555) 253-0000",
			Probability: 1.0,
			Location: &message_types.Location{
				Start: 153, End: 163, Length: 10,
			},
		},
		&message_types.AnalyzeResult{
			Field:       &message_types.FieldTypes{Name: message_types.FieldTypesEnum_PERSON.String()},
			Text:        "John Smith",
			Probability: 0.8,
			Location: &message_types.Location{
				Start: 180, End: 190, Length: 10,
			},
		},
	}
}
