package eventhubs

import (
	"context"
	"time"

	eh "github.com/Azure/azure-event-hubs-go"

	"github.com/Microsoft/presidio/pkg/logger"
	"github.com/Microsoft/presidio/pkg/stream"
)

type eventhubs struct {
	hub         *eh.Hub
	partitionID string
	receiveFunc stream.ReceiveFunc
}

//NewProducer Return new Eventhub for sending messages
func NewProducer(connStr string) stream.Stream {

	hub, err := eh.NewHubFromConnectionString(connStr)
	if err != nil {
		logger.Fatal(err.Error())
	}

	return &eventhubs{
		hub: hub,
	}
}

//TODO: Switch to EPH pattern

//NewConsumer Return new Eventhub for consuming messages
func NewConsumer(connStr string, partitionID string) stream.Stream {

	hub, err := eh.NewHubFromConnectionString(connStr)
	if err != nil {
		logger.Fatal(err.Error())
	}

	return &eventhubs{
		hub:         hub,
		partitionID: partitionID,
	}
}

//TODO: Switch to EPH pattern

//Receive message from eventhub partition.
func (e *eventhubs) Receive(receiveFunc stream.ReceiveFunc) error {
	e.receiveFunc = receiveFunc
	_, err := e.hub.Receive(context.Background(), e.partitionID, e.handleEvent, eh.ReceiveWithLatestOffset())
	return err
}

func (e *eventhubs) handleEvent(ctx context.Context, event *eh.Event) error {
	err := e.receiveFunc(*event.PartitionKey, event.ID, string(event.Data))
	return err
}

//Send message to eventhub
func (e *eventhubs) Send(message string) error {
	ctx, cancel := context.WithTimeout(context.Background(), 20*time.Second)
	defer cancel()
	err := e.hub.Send(ctx, eh.NewEventFromString(message))
	return err
}
