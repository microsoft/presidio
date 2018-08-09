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

func TestDatasinkInit(t *testing.T) {
	var s *server
	datasinkTemplate := &message_types.DatasinkTemplate{}

	// validate datasink is initialized
	_, err := s.Init(context.Background(), datasinkTemplate)
	assert.EqualError(t, err, "datasinkTemplate must me set")

	datasink := &message_types.Datasink{
		DbConfig: &message_types.DBConfig{
			TableName: "name",
		},
	}

	// validate connection string is set
	datasinkTemplate = &message_types.DatasinkTemplate{
		AnalyzerKind: "sqlite3",
		Datasink:     datasink,
	}
	_, err = s.Init(context.Background(), datasinkTemplate)
	assert.EqualError(t, err, "connectionString var must me set")

	// datasinks are empty
	assert.Empty(t, analyzerDatasink)
	assert.Empty(t, anonymizerDatasink)

	datasink.DbConfig.ConnectionString = "./test.db?cache=shared&mode=rwc"

	datasinkTemplate.Datasink = datasink
	s.Init(context.Background(), datasinkTemplate)

	// validate datasink was created successfully
	assert.NotEmpty(t, analyzerDatasink)
	assert.Empty(t, anonymizerDatasink)
}
