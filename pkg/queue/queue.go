package queue

//Queue interface
type Queue interface {
	// Send Message
	Send(message string) error
	// Receive Messages
	Receive(receiveFunc ReceiveFunc)
}

//ReceiveFunc function reference with message data
type ReceiveFunc func(string) error
