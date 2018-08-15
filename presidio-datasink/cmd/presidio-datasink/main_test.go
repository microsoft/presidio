package main

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"

	message_types "github.com/Microsoft/presidio-genproto/golang"
)

func TestDatasinkInit(t *testing.T) {
	var s *server
	datasinkTemplate := &message_types.DatasinkTemplate{}

	// validate datasink is initialized
	_, err := s.Init(context.Background(), datasinkTemplate)
	assert.EqualError(t, err, "AnalyzeDatasink or AnonymizeDatasink must me set")

	datasink := []*message_types.Datasink{
		{
			DbConfig: &message_types.DBConfig{
				TableName: "name",
				Type:      "sqlite3",
			},
		},
	}

	// validate connection string is set
	datasinkTemplate = &message_types.DatasinkTemplate{
		AnalyzeDatasink: datasink,
	}
	_, err = s.Init(context.Background(), datasinkTemplate)
	assert.EqualError(t, err, "connectionString var must me set")

	// datasinks are empty
	assert.Empty(t, analyzerDatasinkArray)
	assert.Empty(t, anonymizerDatasinkArray)

	datasink[0].DbConfig.ConnectionString = "./test.db?cache=shared&mode=rwc"

	datasinkTemplate.AnalyzeDatasink = datasink
	s.Init(context.Background(), datasinkTemplate)

	// validate datasink was created successfully
	assert.Equal(t, 1, len(analyzerDatasinkArray))
	assert.Empty(t, anonymizerDatasinkArray)
}
