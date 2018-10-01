package kafka

import (
	"context"
	"strconv"
	"time"

	"github.com/Shopify/sarama"
	cluster "github.com/bsm/sarama-cluster"

	log "github.com/Microsoft/presidio/pkg/logger"
	"github.com/Microsoft/presidio/pkg/stream"
)

type kafka struct {
	producer sarama.AsyncProducer
	consumer *cluster.Consumer
	ctx      context.Context
	topic    string
}

//NewProducer Return new Kafka Producer stream
func NewProducer(address string, topic string) stream.Stream {

	config := sarama.NewConfig()
	config.Producer.Retry.Max = 5
	// The level of acknowledgement reliability needed from the broker.
	config.Producer.RequiredAcks = sarama.WaitForAll
	brokers := []string{address}
	p, err := sarama.NewAsyncProducer(brokers, config)
	if err != nil {
		log.Fatal(err.Error())
	}

	return &kafka{
		producer: p,
		topic:    topic,
	}
}

//NewConsumer Return new Kafka Consumer stream
func NewConsumer(ctx context.Context, address string, topic string, consumerGroup string) stream.Stream {

	config := cluster.NewConfig()
	config.Consumer.Return.Errors = true
	config.Group.Return.Notifications = true
	config.Consumer.Offsets.Initial = sarama.OffsetOldest

	// init consumer
	brokers := []string{address}
	topics := []string{topic}
	consumer, err := cluster.NewConsumer(brokers, consumerGroup, topics, config)
	if err != nil {
		log.Fatal(err.Error())
	}

	// consume errors
	go func() {
		for err := range consumer.Errors() {
			log.Error("Error: %s\n", err.Error())
		}
	}()

	// consume notifications
	go func() {
		for ntf := range consumer.Notifications() {
			log.Info("Rebalanced: %+v\n", ntf)
		}
	}()

	return &kafka{
		consumer: consumer,
		topic:    topic,
		ctx:      ctx,
	}
}

//Receive message from kafka topic
func (k *kafka) Receive(receiveFunc stream.ReceiveFunc) error {

	for {
		select {
		case <-k.ctx.Done():
			log.Info("Caught signal: terminating")
			return k.consumer.Close()

		case msg, ok := <-k.consumer.Messages():
			if ok {

				err := receiveFunc(k.ctx, strconv.Itoa(int(msg.Partition)), string(msg.Offset), string(msg.Value))
				if err != nil {
					log.Error(err.Error())
				}
				k.consumer.MarkOffset(msg, "") // mark message as processed
			}
		}

		return nil
	}
}

//Send message to kafka topic
func (k *kafka) Send(message string) error {
	var err error

	go func() {

		strTime := strconv.Itoa(int(time.Now().Unix()))
		msg := &sarama.ProducerMessage{
			Topic: k.topic,
			Key:   sarama.StringEncoder(strTime),
			Value: sarama.StringEncoder(message),
		}
		select {
		case k.producer.Input() <- msg:
			log.Info("Delivered message to %v:%v\n", msg.Topic, msg.Partition)
		case err1 := <-k.producer.Errors():
			err = err1.Err
		}
	}()
	return err
}
