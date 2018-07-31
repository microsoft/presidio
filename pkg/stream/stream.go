package stream

//Stream interface
type Stream interface {
	// Send Message
	Send(message string) error
	// Receive Messages
	Receive(receiveFunc ReceiveFunc) error
}

type ReceiveFunc func(string)
