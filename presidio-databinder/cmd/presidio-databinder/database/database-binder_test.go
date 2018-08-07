package databaseBinder

import (
	"testing"

	"github.com/go-xorm/xorm"
	"github.com/stretchr/testify/assert"

	message_types "github.com/Microsoft/presidio-genproto/golang"
)

var (
	// Azure emulator connection string
	dbKind           = "sqlite3"
	connectionString = "./test.db?cache=shared&mode=rwc"
)

func TestResultWrittenToDb(t *testing.T) {
	// Setup
	engine, _ := xorm.NewEngine(dbKind, connectionString)
	tableName := "testTable"
	engine.DropTables(tableName)

	binder := &message_types.Databinder{
		DbConfig: &message_types.DBConfig{
			ConnectionString: connectionString,
			TableName:        tableName,
		},
	}

	databinder := New(binder, dbKind, "analyze")
	resultsPath := "someDir/SomeFile.txt"

	//Act
	mockResult := getAnalyzerMockResult()
	databinder.WriteAnalyzeResults(mockResult, resultsPath)

	//Verify
	var sliceOfAnalyzeResult []analyzerResult
	engine.Table(tableName).Find(&sliceOfAnalyzeResult)

	assert.Equal(t, len(sliceOfAnalyzeResult), 2)
	assert.Equal(t, sliceOfAnalyzeResult[0].Field, sliceOfAnalyzeResult[0].Field)

	// Test Anonymizer
	anonymizeResponse := &message_types.AnonymizeResponse{
		Text: "<Person> live is <Location>",
	}

	engine.DropTables(tableName)
	databinder = New(binder, dbKind, "anonymize")

	// Act
	databinder.WriteAnonymizeResults(anonymizeResponse, resultsPath)

	// Verify
	var sliceOfAnonymizeResult []anonymizerResult
	engine.Table(tableName).Find(&sliceOfAnonymizeResult)

	assert.Equal(t, len(sliceOfAnonymizeResult), 1)
	assert.Equal(t, anonymizeResponse.Text, sliceOfAnonymizeResult[0].AnonymizedText)
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
