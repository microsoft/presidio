// +build integration

package tests

import (
	"context"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"

	log "github.com/Microsoft/presidio/pkg/logger"
	"github.com/Microsoft/presidio/pkg/stream/eventhubs"
)

func TestEventHub(t *testing.T) {

	eventHubConnStr := ""
	storageAccountName := ""
	storageAccountKey := ""
	storageContainerName := ""

	ctx, cancel := context.WithTimeout(context.Background(), time.Duration(time.Second*10))
	defer cancel()

	p := eventhubs.NewProducer(ctx, eventHubConnStr)
	msg := "I live in Zurich and my account number is 2854567876542111"
	err := p.Send(msg)

	assert.NoError(t, err)

	c := eventhubs.NewConsumer(ctx, eventHubConnStr, storageAccountName, storageAccountKey, storageContainerName)

	r := func(ctx context.Context, partition string, seq string, data string) error {
		log.Info("Received: %s,%s,%s", partition, seq, data)
		assert.Equal(t, msg, data)
		return nil
	}

	err = c.Receive(r)
	assert.NoError(t, err)
}
