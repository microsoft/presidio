package database

import (
	"testing"

	"github.com/go-xorm/xorm"
	_ "github.com/mattn/go-sqlite3"
	"github.com/stretchr/testify/assert"

	types "github.com/Microsoft/presidio-genproto/golang"
)

var (
	dbKind           = "sqlite3"
	connectionString = "./test.db?cache=shared&mode=rwc"
)

func TestResultWrittenToDb(t *testing.T) {
	// Setup
	engine, _ := xorm.NewEngine(dbKind, connectionString)
	tableName := "testTable"
	engine.DropTables(tableName)

	sink := &types.Datasink{
		DbConfig: &types.DBConfig{
			ConnectionString: connectionString,
			TableName:        tableName,
			Type:             dbKind,
		},
	}

	datasink := New(sink, "analyze")
	resultsPath := "someDir/SomeFile.txt"

	//Act
	mockResult := getAnalyzerMockResult()
	datasink.WriteAnalyzeResults(mockResult, resultsPath)

	//Verify
	var sliceOfAnalyzeResult []analyzerResult
	engine.Table(tableName).Find(&sliceOfAnalyzeResult)

	assert.Equal(t, len(sliceOfAnalyzeResult), 2)
	assert.Equal(t, sliceOfAnalyzeResult[0].Field, sliceOfAnalyzeResult[0].Field)

	// Test Anonymizer
	anonymizeResponse := &types.AnonymizeResponse{
		Text: "<Person> live is <Location>",
	}

	engine.DropTables(tableName)
	datasink = New(sink, "anonymize")

	// Act
	datasink.WriteAnonymizeResults(anonymizeResponse, resultsPath)

	// Verify
	var sliceOfAnonymizeResult []anonymizerResult
	engine.Table(tableName).Find(&sliceOfAnonymizeResult)

	assert.Equal(t, len(sliceOfAnonymizeResult), 1)
	assert.Equal(t, anonymizeResponse.Text, sliceOfAnonymizeResult[0].AnonymizedText)
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
		&types.AnalyzeResult{
			Field: &types.FieldTypes{Name: types.FieldTypesEnum_PERSON.String()},
			Text:  "John Smith",
			Score: 0.8,
			Location: &types.Location{
				Start: 180, End: 190, Length: 10,
			},
		},
	}
}
