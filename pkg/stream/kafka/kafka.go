package kafka

import (
	"fmt"

	api "github.com/confluentinc/confluent-kafka-go/kafka"

	log "github.com/Microsoft/presidio/pkg/logger"
	"github.com/Microsoft/presidio/pkg/stream"
)

type kafka struct {
	producer *api.Producer
	consumer *api.Consumer
	topic    string
}

//NewProducer Return new Kafka Producer stream
func NewProducer(address string, topic string) stream.Stream {

	p, err := api.NewProducer(&api.ConfigMap{"bootstrap.servers": address})
	if err != nil {
		log.Fatal(err.Error())
	}

	return &kafka{
		producer: p,
		topic:    topic,
	}
}

//NewConsumer Return new Kafka Consumer stream
func NewConsumer(address string, topic string) stream.Stream {

	c, err := api.NewConsumer(&api.ConfigMap{
		"bootstrap.servers": address,
		"group.id":          "presidio",
		"auto.offset.reset": "earliest",
	})

	if err != nil {
		log.Fatal(err.Error())
	}

	err = c.SubscribeTopics([]string{topic}, nil)

	if err != nil {
		log.Fatal(err.Error())
	}

	return &kafka{
		consumer: c,
		topic:    topic,
	}
}

//Receive message from kafka topic
func (k *kafka) Receive(receiveFunc stream.ReceiveFunc) error {

	for {
		msg, err := k.consumer.ReadMessage(-1)
		if err != nil {
			return err
		}
		receiveFunc(string(msg.Value))
	}
	return nil
}

//Send message to kafka topic
func (k *kafka) Send(message string) error {

	// Delivery report handler for produced messages
	go func() {
		for e := range k.producer.Events() {
			switch ev := e.(type) {
			case *api.Message:
				if ev.TopicPartition.Error != nil {
					log.Error(fmt.Sprintf("Delivery failed: %v\n", ev.TopicPartition))
				} else {
					log.Info(fmt.Sprintf("Delivered message to %v\n", ev.TopicPartition))
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
