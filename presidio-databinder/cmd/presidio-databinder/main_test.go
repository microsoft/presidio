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

func TestDataBinderInit(t *testing.T) {
	var s *server
	databinderTemplate := &message_types.DatabinderTemplate{}

	// validate databinder is initialized
	_, err := s.Init(context.Background(), databinderTemplate)
	assert.EqualError(t, err, "databinderTemplate must me set")

	databinder := [](*message_types.Databinder){
		&message_types.Databinder{
			BindType: "sqlite3",
		},
	}

	// validate connection string is set
	databinderTemplate.Databinder = databinder
	_, err = s.Init(context.Background(), databinderTemplate)
	assert.EqualError(t, err, "connectionString var must me set")

	// databinders array is empty
	assert.Empty(t, databinderArray)

	databinder[0].ConnectionString = "./test.db?cache=shared&mode=rwc"
	databinderTemplate.Databinder = databinder
	s.Init(context.Background(), databinderTemplate)

	// validate databinder was created successfully
	assert.Equal(t, len(databinderArray), 1)
}
