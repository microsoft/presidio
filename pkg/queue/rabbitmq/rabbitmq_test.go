package rabbitmq

// import (
// 	"context"
// 	"testing"
// 	"time"

// 	"github.com/stretchr/testify/assert"

// 	log "github.com/Microsoft/presidio/pkg/logger"
// )

// func TestSendReceive(t *testing.T) {

// 	ctx, cancel := context.WithTimeout(context.Background(), time.Second*10)
// 	defer cancel()

// 	r := New(ctx, "amqp://user:bitnami@localhost:5672/", "test")
// 	msg := "test"
// 	err := r.Send(msg)
// 	assert.NoError(t, err)

// 	rc := func(data string) error {
// 		log.Info("Received: %s", data)
// 		assert.Equal(t, msg, data)
// 		return nil
// 	}
// 	r.Receive(rc)
// }
