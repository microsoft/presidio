package eventhubs

import (
	"context"
	"time"

	api "github.com/Azure/azure-event-hubs-go"

	"github.com/presid-io/presidio/pkg/logger"
	"github.com/presid-io/presidio/pkg/stream"
)

type eventhubs struct {
	hub *api.Hub
}

//New Return new Eventhub stream
func New() stream.Stream {

	hub, err := api.NewHubFromEnvironment()
	if err != nil {
		logger.Fatal(err.Error())
	}

	return &eventhubs{
		hub: hub,
	}
}

//Send message to eventhub
func (e *eventhubs) Send(message string) error {
	ctx, cancel := context.WithTimeout(context.Background(), 20*time.Second)
	defer cancel()
	err := e.hub.Send(ctx, api.NewEventFromString(message))
	return err
}
