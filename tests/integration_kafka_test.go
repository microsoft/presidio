// +build functional

package tests

import (
	//"github.com/Microsoft/presidio/pkg/stream"
	"context"
	"testing"
	"time"

	"github.com/satori/go.uuid"
	"github.com/stretchr/testify/assert"

	log "github.com/Microsoft/presidio/pkg/logger"
	"github.com/Microsoft/presidio/pkg/stream/kafka"
)

const address = "localhost"
const topic = "presidio-topic"

func TestKafka(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), time.Duration(time.Second*10))
	defer cancel()

	p := kafka.NewProducer(address, topic)
	msg := uuid.NewV4().String()
	err := p.Send(msg)
	if err != nil {
		t.Fatal(err)
	}

	c := kafka.NewConsumer(ctx, address, topic)

	r := func(partition string, seq string, data string) error {
		log.Info("Received: %s,%s,%s", partition, seq, data)
		assert.Equal(t, msg, data)
		return nil
	}

	err = c.Receive(r)
	if err != nil {
		t.Fatal(err)
	}
}
