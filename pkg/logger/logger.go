package logger

import (
	"os"
	"strings"

	"github.com/spf13/pflag"
	"github.com/spf13/viper"

	"go.uber.org/zap"
	"go.uber.org/zap/zapcore"
	"go.uber.org/zap/zaptest/observer"
)

var sugaredLogger *zap.SugaredLogger
var logger *zap.Logger

func init() {
	pflag.String("log_level", "info", "Log level - debug/info/warn/error")
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

	viper.AutomaticEnv()
	logLevel := viper.GetString("LOG_LEVEL")

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
	if logger == nil {
		initLogger()
	}
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
	if sugaredLogger == nil {
		initLogger()
	}
	sugaredLogger.Debugf(message, fields...)
}

// Info logs a debug message with the given fields
func Info(message string, fields ...interface{}) {
	if sugaredLogger == nil {
		initLogger()
	}
	sugaredLogger.Infof(message, fields...)
}

// Warn logs a debug message with the given fields
func Warn(message string, fields ...interface{}) {
	if sugaredLogger == nil {
		initLogger()
	}
	sugaredLogger.Warnf(message, fields...)
}

// Error logs a debug message with the given fields
func Error(message string, fields ...interface{}) {
	if sugaredLogger == nil {
		initLogger()
	}
	sugaredLogger.Errorf(message, fields...)
}

// Fatal logs a message than calls os.Exit(1)
func Fatal(message string, fields ...interface{}) {
	if sugaredLogger == nil {
		initLogger()
	}
	sugaredLogger.Fatalf(message, fields...)
	sugaredLogger.Sync()
	os.Exit(1)
}
