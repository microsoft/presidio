// +build integration

package tests

import (
	"context"
	"testing"
	"time"

	"github.com/satori/go.uuid"
	"github.com/stretchr/testify/assert"

	log "github.com/Microsoft/presidio/pkg/logger"
	"github.com/Microsoft/presidio/pkg/stream/kafka"
)

func TestKafka(t *testing.T) {

	address := "localhost:9092"
	topic := "presidio-topic"
	cg := "presidio-cg"

	ctx, cancel := context.WithTimeout(context.Background(), time.Duration(time.Second*10))
	defer cancel()

	p := kafka.NewProducer(address, topic)
	msg := uuid.NewV4().String()
	p.Send(msg)

	c := kafka.NewConsumer(ctx, address, topic, cg)

	r := func(ctx context.Context, partition string, seq string, data string) error {
		log.Info("Received: %s,%s,%s", partition, seq, data)
		assert.Equal(t, msg, data)
		return nil
	}

	err := c.Receive(r)
	assert.NoError(t, err)
}
