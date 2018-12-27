package logger

import (
	"os"
	"strings"
	"sync"

	"go.uber.org/zap"
	"go.uber.org/zap/zapcore"
	"go.uber.org/zap/zaptest/observer"
)

var once sync.Once

func init() {
	// once ensures the singleton is initialized only once
	once.Do(func() {
		CreateLogger("debug")
	})
}

//CreateLogger with specific log level
func CreateLogger(logLevel string) {

	level := getLogLevel(logLevel)
	alevel := zap.NewAtomicLevelAt(level)

	var config zap.Config
	if level == zapcore.DebugLevel {
		config = zap.NewDevelopmentConfig()
	} else {
		config = zap.NewProductionConfig()
	}
	config.EncoderConfig.EncodeLevel = zapcore.CapitalColorLevelEncoder
	config.DisableStacktrace = true
	config.DisableCaller = true
	config.Level = alevel

	logger, err := config.Build()
	zap.ReplaceGlobals(logger)

	if err != nil {
		panic(err.Error())
	}
}

func getLogLevel(logLevel string) zapcore.Level {
	switch strings.ToLower(logLevel) {
	case "debug":
		return zapcore.DebugLevel
	case "info":
		return zapcore.InfoLevel
	case "warn":
		return zapcore.WarnLevel
	case "error":
		return zapcore.ErrorLevel
	case "dpanic":
		return zapcore.DPanicLevel
	case "panic":
		return zapcore.PanicLevel
	case "fatal":
		return zapcore.FatalLevel
	default:
		return zapcore.InfoLevel
	}
}

// GetLogger get native not sugared logger
func GetLogger() *zap.Logger {
	return zap.L()
}

// ObserveLogging constructs a logger through the zap/zaptest/observer framework
// so that logs will be accessible in tests.
func ObserveLogging(level zapcore.Level) *observer.ObservedLogs {
	observedLogger, logs := observer.New(level)
	logger := zap.New(observedLogger)
	zap.ReplaceGlobals(logger)
	return logs
}

// Debug logs a debug message with the given fields
func Debug(message string, fields ...interface{}) {
	zap.S().Debugf(message, fields...)
}

// Info logs a debug message with the given fields
func Info(message string, fields ...interface{}) {
	zap.S().Infof(message, fields...)
}

// Warn logs a debug message with the given fields
func Warn(message string, fields ...interface{}) {
	zap.S().Warnf(message, fields...)
}

// Error logs a debug message with the given fields
func Error(message string, fields ...interface{}) {
	zap.S().Errorf(message, fields...)
}

// Fatal logs a message than calls os.Exit(1)
func Fatal(message string, fields ...interface{}) {
	zap.S().Fatalf(message, fields...)
	zap.S().Sync()
	os.Exit(1)
}
