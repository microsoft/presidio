package rabbitmq

import (
	"context"

	"github.com/streadway/amqp"

	log "github.com/Microsoft/presidio/pkg/logger"
	"github.com/Microsoft/presidio/pkg/queue"
)

type rabbitmq struct {
	conn    *amqp.Connection
	channel *amqp.Channel
	queue   string
	ctx     context.Context
}

//New rabbitmq
func New(ctx context.Context, connStr string, queue string) queue.Queue {

	conn, err := amqp.Dial(connStr)
	if err != nil {
		log.Fatal("Failed to connect to RabbitMQ - %s", err.Error())
	}

	ch, err := conn.Channel()
	if err != nil {
		log.Fatal("Failed to open a channel - %s", err.Error())
	}

	q, err := ch.QueueDeclare(
		queue, // name
		true,  // durable
		false, // delete when unused
		false, // exclusive
		false, // no-wait
		nil,   // arguments
	)
	if err != nil {
		log.Fatal("Failed to declare a queue - %s", err.Error())
	}

	err = ch.Qos(
		1,     // prefetch count
		0,     // prefetch size
		false, // global
	)
	if err != nil {
		log.Fatal("Failed to set QoS - %s", err.Error())
	}

	return &rabbitmq{
		conn:    conn,
		channel: ch,
		queue:   q.Name,
		ctx:     ctx,
	}
}

func (r *rabbitmq) Send(message string) error {

	err := r.channel.Publish(
		"",      // exchange
		r.queue, // routing key
		false,   // mandatory
		false,
		amqp.Publishing{
			DeliveryMode: amqp.Persistent,
			ContentType:  "text/plain",
			Body:         []byte(message),
		})

	return err

}

func (r *rabbitmq) Receive(receiveFunc queue.ReceiveFunc) {

	msgs, err := r.channel.Consume(
		r.queue, // queue
		"",      // consumer
		false,   // auto-ack
		false,   // exclusive
		false,   // no-local
		false,   // no-wait
		nil,     // args
	)
	if err != nil {
		log.Fatal("Failed to register a consumer - %s", err.Error())
	}

	for {
		select {
		case <-r.ctx.Done():
			log.Info("Caught signal: terminating")
			r.closeRabbitMqConnection()
			return
		case msg := <-msgs:
			err := receiveFunc(string(msg.Body))
			if err != nil {
				log.Error("Message error - %s", err.Error())
			} else {
				err := msg.Ack(false)
				if err != nil {
					log.Error("Message Ack error - %s", err.Error())
				}
			}
		}
	}
}

func (r *rabbitmq) closeRabbitMqConnection() {
	err := r.conn.Close()
	if err != nil {
		log.Error(err.Error())
	}
}
