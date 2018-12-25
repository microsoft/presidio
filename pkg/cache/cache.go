package cache

//Cache interface
type Cache interface {
	Set(key string, value string) error
	Get(key string) (string, error)
	Delete(key string) error
}
