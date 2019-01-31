package eventhubs

import (
	"context"
	"time"

	"github.com/Azure/azure-amqp-common-go/conn"
	"github.com/Azure/azure-amqp-common-go/sas"
	eh "github.com/Azure/azure-event-hubs-go"
	"github.com/Azure/azure-event-hubs-go/eph"
	"github.com/Azure/azure-event-hubs-go/storage"
	"github.com/Azure/azure-storage-blob-go/azblob"
	"github.com/Azure/go-autorest/autorest/azure"

	log "github.com/Microsoft/presidio/pkg/logger"
	"github.com/Microsoft/presidio/pkg/stream"
)

type eventhubs struct {
	hub         *eh.Hub
	eph         *eph.EventProcessorHost
	receiveFunc stream.ReceiveFunc
	ctx         context.Context
}

//NewProducer Return new Eventhub for sending messages
func NewProducer(ctx context.Context, connStr string) stream.Stream {

	hub, err := eh.NewHubFromConnectionString(connStr)
	if err != nil {
		log.Fatal(err.Error())
	}

	return &eventhubs{
		hub: hub,
		ctx: ctx,
	}
}

//NewConsumer Return new Eventhub for consuming messages
func NewConsumer(ctx context.Context, eventHubConnStr string, storageAccountName string, storageAccountKey string, storageContainerName string) stream.Stream {

	// Azure Event Hub connection string
	parsed, err := conn.ParsedConnectionFromStr(eventHubConnStr)
	if err != nil {
		log.Fatal(err.Error())
	}
	// SAS token provider for Azure Event Hubs
	provider, err := sas.NewTokenProvider(sas.TokenProviderWithKey(parsed.KeyName, parsed.Key))
	if err != nil {
		log.Fatal(err.Error())
	}
	// create a new Azure Storage Leaser / Checkpointer
	cred, err := azblob.NewSharedKeyCredential(storageAccountName, storageAccountKey)
	if err != nil {
		log.Fatal(err.Error())
	}

	leaserCheckpointer, err := storage.NewStorageLeaserCheckpointer(cred, storageAccountName, storageContainerName, azure.PublicCloud)
	if err != nil {
		log.Fatal(err.Error())
	}

	// create a new EPH processor
	hub, err := eph.New(ctx, parsed.Namespace, parsed.HubName, provider, leaserCheckpointer, leaserCheckpointer)
	if err != nil {
		log.Fatal(err.Error())
	}

	return &eventhubs{
		eph: hub,
		ctx: ctx,
	}
}

//Receive message from eventhub partition.
func (e *eventhubs) Receive(receiveFunc stream.ReceiveFunc) error {

	e.receiveFunc = receiveFunc
	_, err := e.eph.RegisterHandler(e.ctx, e.handleEvent)
	if err != nil {
		return err
	}

	return e.eph.Start(e.ctx)
}

func (e *eventhubs) handleEvent(ctx context.Context, event *eh.Event) error {
	key := "-1"
	if event.PartitionKey != nil {
		key = *event.PartitionKey
	}
	return e.receiveFunc(ctx, key, event.ID, string(event.Data))
}

//Send message to eventhub
func (e *eventhubs) Send(message string) error {
	ctx, cancel := context.WithTimeout(e.ctx, 10*time.Second)
	defer cancel()
	return e.hub.Send(ctx, eh.NewEventFromString(message))
}
