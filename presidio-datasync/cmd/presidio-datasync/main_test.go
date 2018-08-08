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

func TestDataSyncInit(t *testing.T) {
	var s *server
	dataSyncTemplate := &message_types.DataSyncTemplate{}

	// validate dataSync is initialized
	_, err := s.Init(context.Background(), dataSyncTemplate)
	assert.EqualError(t, err, "dataSyncTemplate must me set")

	dataSync := &message_types.DataSync{
		DbConfig: &message_types.DBConfig{
			TableName: "name",
		},
	}

	// validate connection string is set
	dataSyncTemplate = &message_types.DataSyncTemplate{
		AnalyzerKind: "sqlite3",
		DataSync:     dataSync,
	}
	_, err = s.Init(context.Background(), dataSyncTemplate)
	assert.EqualError(t, err, "connectionString var must me set")

	// dataSyncs are empty
	assert.Empty(t, analyzerDataSync)
	assert.Empty(t, anonymizerDataSync)

	dataSync.DbConfig.ConnectionString = "./test.db?cache=shared&mode=rwc"

	dataSyncTemplate.DataSync = dataSync
	s.Init(context.Background(), dataSyncTemplate)

	// validate dataSync was created successfully
	assert.NotEmpty(t, analyzerDataSync)
	assert.Empty(t, anonymizerDataSync)
}
