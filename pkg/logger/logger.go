package logger

import (
	"os"
	"strings"
	"sync"

	"go.uber.org/zap"
	"go.uber.org/zap/zapcore"
	"go.uber.org/zap/zaptest/observer"
)

var sugaredLogger *zap.SugaredLogger
var logger *zap.Logger

//var logs *observer.ObservedLogs
var once sync.Once

// Init initializes a thread-safe singleton logger
// This would be called from a main method when the application starts up
// This function would ideally, take zap configuration, but is left out
// in favor of simplicity using the example logger.
func init() {
	// once ensures the singleton is initialized only once
	once.Do(func() {
		initLogger()
	})
}

func initLogger() {
	logLevel := getLogLevel()
	level := zap.NewAtomicLevelAt(logLevel)

	var config zap.Config
	if logLevel == zapcore.DebugLevel {
		config = zap.NewDevelopmentConfig()
	} else {
		config = zap.NewProductionConfig()
	}
	config.EncoderConfig.EncodeLevel = zapcore.CapitalColorLevelEncoder
	config.DisableStacktrace = true
	config.DisableCaller = true
	config.Level = level

	build, err := config.Build()
	logger = build
	sugaredLogger = build.Sugar()
	if err != nil {
		panic(err.Error())
	}
}
func getLogLevel() zapcore.Level {

	logLevel := os.Getenv("LOG_LEVEL")
	switch strings.ToLower(logLevel) {
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
		return zapcore.DebugLevel
	}
}

// GetLogger get native not sugared logger
func GetLogger() *zap.Logger {
	return logger
}

// ObserveLogging constructs a logger through the zap/zaptest/observer framework
// so that logs will be accessible in tests.
func ObserveLogging(level zapcore.Level) *observer.ObservedLogs {
	observedLogger, logs := observer.New(level)
	sugaredLogger = zap.New(observedLogger).With().Sugar()
	return logs
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
