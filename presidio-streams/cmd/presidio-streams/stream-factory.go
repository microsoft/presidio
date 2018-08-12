package main

import (
	"github.com/Microsoft/presidio/pkg/stream"
	"github.com/Microsoft/presidio/pkg/stream/eventhubs"
	"github.com/Microsoft/presidio/pkg/stream/kafka"
	"github.com/Microsoft/presidio/pkg/stream/kinesis"
)

func createStream() stream.Stream {
	config := streamRequest.GetStreamConfig()
	if streamRequest.GetKind() == "kafka" && config.KafkaConfig != nil {
		k := kafka.NewConsumer(config.KafkaConfig.GetAddress(), config.KafkaConfig.GetTopic())
		return k
	}

	if streamRequest.GetKind() == "eventhub" && config.EhConfig != nil {
		e := eventhubs.NewConsumer("", "")
		return e
	}
	if streamRequest.GetKind() == "kinesis" && config.EhConfig != nil {
		k := kinesis.NewConsumer("", "")
		return k
	}
	return nil
}
