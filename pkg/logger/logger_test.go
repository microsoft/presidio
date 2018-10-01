package logger

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"go.uber.org/zap"
)

func TestDebug(t *testing.T) {
	logs := ObserveLogging(zap.DebugLevel)
	Debug("test debug log")
	assert.Equal(t, 1, len(logs.TakeAll()))
}

func TestLevels(t *testing.T) {
	logs := ObserveLogging(zap.InfoLevel)
	Debug("test debug log")
	Info("test info level")
	l := logs.TakeAll()
	assert.Equal(t, 1, len(l))
	assert.Equal(t, zap.InfoLevel, l[0].Level)
}
