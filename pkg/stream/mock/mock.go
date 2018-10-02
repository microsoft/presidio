package mock

import (
	"context"

	"github.com/satori/go.uuid"

	log "github.com/Microsoft/presidio/pkg/logger"
	"github.com/Microsoft/presidio/pkg/stream"
)

type mock struct {
	stream mockImpl
	topic  string
}

type mockImpl struct {
	partitions map[string][]string
}

type mockMessage struct {
	Value     string
	Key       string
	Partition string
}

//New Return new Mock Producer stream
func New(topic string) stream.Stream {

	m := mockImpl{}
	err := m.New(topic)

	if err != nil {
		log.Fatal(err.Error())
	}

	return &mock{
		stream: m,
		topic:  topic,
	}
}

//Receive message from mock topic
func (m *mock) Receive(receiveFunc stream.ReceiveFunc) error {

	for {
		msg, err := m.stream.Receive()
		if err != nil {
			return err
		}
		if msg == nil {
			break
		}

		err = receiveFunc(context.Background(), msg.Partition, msg.Key, msg.Value)
		if err != nil {
			log.Error(err.Error())
		}

	}
	return nil
}

//Send message to mock topic
func (m *mock) Send(message string) error {
	err := m.stream.Send(message)
	return err

}

// Mock impl
func (m *mockImpl) Send(message string) error {

	log.Info("Sending: %s", message)
	m.partitions["1"] = append(m.partitions["0"], message)
	return nil
}

func (m *mockImpl) New(topic string) error {
	m.partitions = make(map[string][]string, 1)
	m.partitions["1"] = make([]string, 0)
	log.Info("New topic: %s", topic)
	return nil
}

func (m *mockImpl) Receive() (*mockMessage, error) {
	var value string
	if len(m.partitions["1"]) == 0 {
		return nil, nil
	}
	value, m.partitions["1"] = m.partitions["1"][0], m.partitions["1"][1:]

	msg := mockMessage{
		Partition: "1",
		Value:     value,
		Key:       uuid.NewV4().String(),
	}
	return &msg, nil
}
