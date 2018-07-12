package kafka

import (
	"fmt"

	api "github.com/confluentinc/confluent-kafka-go/kafka"

	"github.com/presid-io/presidio/pkg/logger"
	"github.com/presid-io/presidio/pkg/stream"
)

type kafka struct {
	producer *api.Producer
	topic    string
}

//New Return new Kafka stream
func New(address string, topic string) stream.Stream {

	p, err := api.NewProducer(&api.ConfigMap{"bootstrap.servers": address})
	if err != nil {
		logger.Fatal(err.Error())
	}

	return &kafka{
		producer: p,
		topic:    topic,
	}
}

//Send message to kafka topic
func (k *kafka) Send(message string) error {

	// Delivery report handler for produced messages
	go func() {
		for e := range k.producer.Events() {
			switch ev := e.(type) {
			case *api.Message:
				if ev.TopicPartition.Error != nil {
					logger.Error(fmt.Sprintf("Delivery failed: %v\n", ev.TopicPartition))
				} else {
					logger.Info(fmt.Sprintf("Delivered message to %v\n", ev.TopicPartition))
				}
			}
		}
	}()

	err := k.producer.Produce(&api.Message{
		TopicPartition: api.TopicPartition{Topic: &k.topic, Partition: api.PartitionAny},
		Value:          []byte(message),
	}, nil)

	return err

}
