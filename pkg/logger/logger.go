package logger

import (
	"os"
	"sync"

	"go.uber.org/zap"
	"go.uber.org/zap/zapcore"
)

var singleton *zap.Logger
var once sync.Once

// Init initializes a thread-safe singleton logger
// This would be called from a main method when the application starts up
// This function would ideally, take zap configuration, but is left out
// in favor of simplicity using the example logger.
func init() {
	// once ensures the singleton is initialized only once
	once.Do(func() {
		var err error
		level := zap.NewAtomicLevelAt(zap.DebugLevel)
		config := zap.NewDevelopmentConfig()
		config.EncoderConfig.EncodeLevel = zapcore.CapitalColorLevelEncoder
		config.DisableStacktrace = true
		config.Level = level
		singleton, err = config.Build()
		if err != nil {
			panic(err.Error())
		}
	})
}

//GetInstance export zap instance
func GetInstance() *zap.Logger {
	return singleton
}

// Debug logs a debug message with the given fields
func Debug(message string, fields ...zap.Field) {
	singleton.Debug(message, fields...)
}

// Info logs a debug message with the given fields
func Info(message string, fields ...zap.Field) {
	singleton.Info(message, fields...)
}

// Warn logs a debug message with the given fields
func Warn(message string, fields ...zap.Field) {
	singleton.Warn(message, fields...)
}

// Error logs a debug message with the given fields
func Error(message string, fields ...zap.Field) {
	singleton.Error(message, fields...)
}

// Fatal logs a message than calls os.Exit(1)
func Fatal(message string, fields ...zap.Field) {
	singleton.Fatal(message, fields...)
	os.Exit(1)
}
