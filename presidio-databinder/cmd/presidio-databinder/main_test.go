package main

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"

	message_types "github.com/Microsoft/presidio-genproto/golang"
)

func TestIsDatabase(t *testing.T) {
	assert.True(t, isDatabase("mssql"))
	assert.True(t, isDatabase("mysql"))
	assert.True(t, isDatabase("oracle"))
	assert.True(t, isDatabase("postgres"))
	assert.True(t, isDatabase("sqlite3"))
	assert.False(t, isDatabase("kafka"))
}

func TestIsCloudStorage(t *testing.T) {
	assert.True(t, isCloudStorage("s3"))
	assert.True(t, isCloudStorage("azureblob"))
	assert.True(t, isCloudStorage("googlestorage"))
	assert.False(t, isCloudStorage("postgres"))
}

func TestDataBinderInit(t *testing.T) {
	var s *server
	databinderTemplate := &message_types.DatabinderTemplate{}

	// validate databinder is initialized
	_, err := s.Init(context.Background(), databinderTemplate)
	assert.EqualError(t, err, "databinderTemplate must me set")

	databinder := &message_types.Databinder{
		DbConfig: &message_types.DBConfig{
			TableName: "name",
		},
	}

	// validate connection string is set
	databinderTemplate = &message_types.DatabinderTemplate{
		AnalyzerKind: "sqlite3",
		Databinder:   databinder,
	}
	_, err = s.Init(context.Background(), databinderTemplate)
	assert.EqualError(t, err, "connectionString var must me set")

	// databinders are empty
	assert.Empty(t, analyzerDataBinder)
	assert.Empty(t, anonymizerDataBinder)

	databinder.DbConfig.ConnectionString = "./test.db?cache=shared&mode=rwc"

	databinderTemplate.Databinder = databinder
	s.Init(context.Background(), databinderTemplate)

	// validate databinder was created successfully
	assert.NotEmpty(t, analyzerDataBinder)
	assert.Empty(t, anonymizerDataBinder)
}
