package logger

import (
	"os"
	"sync"

	"go.uber.org/zap"
	"go.uber.org/zap/zapcore"
)

var sugaredLogger *zap.SugaredLogger
var logger *zap.Logger

var once sync.Once

// Init initializes a thread-safe singleton logger
// This would be called from a main method when the application starts up
// This function would ideally, take zap configuration, but is left out
// in favor of simplicity using the example logger.
func init() {
	// once ensures the singleton is initialized only once
	once.Do(func() {
		level := zap.NewAtomicLevelAt(zap.DebugLevel)
		config := zap.NewDevelopmentConfig()
		config.EncoderConfig.EncodeLevel = zapcore.CapitalColorLevelEncoder
		config.DisableStacktrace = true
		config.Level = level
		config.DisableCaller = true

		build, err := config.Build()
		logger = build
		sugaredLogger = build.Sugar()
		if err != nil {
			panic(err.Error())
		}
	})
}

func GetLogger() *zap.Logger {
	return logger
}

// Debug logs a debug message with the given fields
func Debug(message string, fields ...interface{}) {
	sugaredLogger.Debugf(message, fields...)
}

// Info logs a debug message with the given fields
func Info(message string, fields ...interface{}) {
	sugaredLogger.Infof(message, fields...)
}

// Warn logs a debug message with the given fields
func Warn(message string, fields ...interface{}) {
	sugaredLogger.Warnf(message, fields...)
}

// Error logs a debug message with the given fields
func Error(message string, fields ...interface{}) {
	sugaredLogger.Errorf(message, fields...)
}

// Fatal logs a message than calls os.Exit(1)
func Fatal(message string, fields ...interface{}) {
	sugaredLogger.Fatalf(message, fields...)
	os.Exit(1)
}
