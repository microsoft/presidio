package kafka

import (
	"context"
	"strconv"

	api "github.com/confluentinc/confluent-kafka-go/kafka"

	log "github.com/Microsoft/presidio/pkg/logger"
	"github.com/Microsoft/presidio/pkg/stream"
)

type kafka struct {
	producer *api.Producer
	consumer *api.Consumer
	ctx      context.Context
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
func NewConsumer(ctx context.Context, address string, topic string) stream.Stream {

	c, err := api.NewConsumer(&api.ConfigMap{
		"bootstrap.servers":               address,
		"group.id":                        "presidio",
		"session.timeout.ms":              6000,
		"go.events.channel.enable":        true,
		"go.application.rebalance.enable": true,
		"default.topic.config":            api.ConfigMap{"auto.offset.reset": "earliest"},
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
		ctx:      ctx,
	}
}

//Receive message from kafka topic
func (k *kafka) Receive(receiveFunc stream.ReceiveFunc) error {

	run := true

	for run {
		select {
		case <-k.ctx.Done():
			log.Info("Caught signal: terminating")
			run = false
		case ev := <-k.consumer.Events():
			switch e := ev.(type) {
			case api.AssignedPartitions:
				log.Info("%% %v\n", e)
				err := k.consumer.Assign(e.Partitions)
				if err != nil {
					log.Error(err.Error())
				}
			case api.RevokedPartitions:
				log.Info("%% %v\n", e)
				err := k.consumer.Unassign()
				if err != nil {
					log.Error(err.Error())
				}
			case *api.Message:
				err := receiveFunc(strconv.Itoa(int(e.TopicPartition.Partition)), string(e.Key), string(e.Value))
				if err != nil {
					log.Error(err.Error())
				}
			case api.PartitionEOF:
				log.Info("%% Reached %v\n", e)
			case api.Error:
				run = false
				return e
			}
		}
	}
	err := k.consumer.Close()
	if err != nil {
		log.Error(err.Error())
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
					log.Error("Delivery failed: %v\n", ev.TopicPartition)
				} else {
					log.Info("Delivered message to %v\n", ev.TopicPartition)
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
