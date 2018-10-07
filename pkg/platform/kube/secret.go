package kube

import (
	"fmt"

	apiv1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

func (s *store) GetKVPair(key string) (string, error) {

	secrets := s.client.CoreV1().Secrets(s.namespace)

	secret, err := secrets.Get(key, metav1.GetOptions{})

	if err != nil {
		return "", err
	}

	for k, v := range secret.Data {
		if k == key {
			return string(v), nil
		}
	}

	for k, v := range secret.StringData {
		if k == key {
			return v, nil
		}
	}
	return "", fmt.Errorf("Key in secret not found")

}

func (s *store) PutKVPair(key string, value string) error {

	secrets := s.client.CoreV1().Secrets(s.namespace)

	secret := &apiv1.Secret{
		ObjectMeta: metav1.ObjectMeta{
			Name: key,
		},
		StringData: map[string]string{
			key: value,
		},
	}

	_, err := secrets.Get(key, metav1.GetOptions{})
	if err != nil {
		_, err = secrets.Create(secret)
		return err
	}
	_, err = secrets.Update(secret)
	return err
}

func (s *store) DeleteKVPair(key string) error {

	secrets := s.client.CoreV1().Secrets(s.namespace)

	_, err := secrets.Get(key, metav1.GetOptions{})
	if err != nil {
		return err
	}
	err = secrets.Delete(key, &metav1.DeleteOptions{})
	return err

}
