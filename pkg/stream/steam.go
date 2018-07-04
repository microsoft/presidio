package stream

//Stream interface
type Stream interface {
	// Send Message
	Send(message string) error
}
