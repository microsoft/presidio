package main

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestIsDatabase(t *testing.T) {
	assert.True(t, isDatabase("mysql"))
	assert.True(t, isDatabase("oracle"))
	assert.True(t, isDatabase("mssql"))
	assert.True(t, isDatabase("postgres"))
	assert.False(t, isDatabase("kafka"))
}
