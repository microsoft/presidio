package stream

import (
	"context"
)

//Stream interface
type Stream interface {
	// Send Message
	Send(message string) error
	// Receive Messages
	Receive(receiveFunc ReceiveFunc) error
}

//ReceiveFunc function reference with partition_id sequence number and message data
type ReceiveFunc func(context.Context, string, string, string) error
