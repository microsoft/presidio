package main

import (
	"context"
	"crypto/md5"
	"encoding/json"
	"errors"
	"sync"

	"google.golang.org/grpc/reflection"

	"flag"

	"github.com/spf13/pflag"
	"github.com/spf13/viper"

	types "github.com/Microsoft/presidio-genproto/golang"

	"encoding/hex"

	"github.com/Microsoft/presidio/pkg/cache"
	log "github.com/Microsoft/presidio/pkg/logger"
	"github.com/Microsoft/presidio/pkg/platform"
	"github.com/Microsoft/presidio/pkg/presidio/services"
	"github.com/Microsoft/presidio/pkg/rpc"
)

type server struct{}

var (
	settings         *platform.Settings
	recognizersStore cache.Cache
)

var (
	recognizersKey = "custom_recognizers"
	hashKey        = "custom_recognizers:hash"
)

var mutex sync.RWMutex

func main() {

	pflag.Int(platform.GrpcPort, 3004, "GRPC listen port")
	pflag.String(platform.RedisURL, "localhost:6379", "Redis address")
	pflag.String(platform.RedisPassword, "", "Redis db password (optional)")
	pflag.Int(platform.RedisDb, 0, "Redis db (optional)")
	pflag.Bool(platform.RedisSSL, false, "Redis ssl (optional)")
	pflag.String(platform.PresidioNamespace, "", "Presidio Kubernetes namespace (optional)")
	pflag.String("log_level", "info", "Log level - debug/info/warn/error")

	pflag.CommandLine.AddGoFlagSet(flag.CommandLine)
	pflag.Parse()
	viper.BindPFlags(pflag.CommandLine)

	settings = platform.GetSettings()
	log.CreateLogger(settings.LogLevel)

	svc := services.New(settings)

	if settings.RedisURL != "" {
		recognizersStore = svc.SetupCache()
	}

	lis, s := rpc.SetupClient(settings.GrpcPort)

	types.RegisterRecognizersStoreServiceServer(s, &server{})
	reflection.Register(s)

	if err := s.Serve(lis); err != nil {
		log.Fatal(err.Error())
	}
}

// Acquires (or block until acquires) the lock to be able to write custom
// recognizers
func writersLock() {
	log.Info("Acquiring lock")
	mutex.Lock()
	log.Info("Acquired")
}

// Releases the writers lock
func writersUnlock() {
	log.Info("Releasing lock")
	mutex.Unlock()
	log.Info("Released")
}

// setValue sets the recognizers array in the store and updates the hash
func setValue(value []byte) error {
	err := recognizersStore.Set(recognizersKey, string(value))
	if err != nil {
		log.Error(err.Error())
		return err
	}

	hashVal := md5.Sum(value)
	calculatedHash := hex.EncodeToString(hashVal[:])
	log.Info("Updating hash: " + calculatedHash)
	err = recognizersStore.Set(hashKey, calculatedHash)
	if err != nil {
		log.Error(err.Error())
		return err
	}

	return nil
}

func getExistingRecognizers() ([]types.PatternRecognizer, error) {
	recognizersArr := make([]types.PatternRecognizer, 0)
	existingItems, err := recognizersStore.Get(recognizersKey)
	if err == nil && existingItems != "" {
		log.Info("Found existing recognizers...")
		var recognizers []types.PatternRecognizer
		err = json.Unmarshal([]byte(existingItems), &recognizers)
		if err != nil {
			return nil, err
		}
		recognizersArr = append(recognizersArr, recognizers...)
	}
	return recognizersArr, nil
}

// InsertOrUpdateRecognizer inserts (or updated) a recognizer to the store
func insertOrUpdateRecognizer(value string, isUpdate bool) error {
	if recognizersStore == nil {
		return errors.New("cache is missing")
	}

	// When updating the underlying storage we want to ensure mutual
	// exclusivness. To avoid situtation of two concurrent updates that creates
	// a race condition. Resulting in a custom recognizer data loss
	writersLock()
	defer writersUnlock()
	existingRecognizersArr, err := getExistingRecognizers()
	if err != nil {
		return err
	}

	var newRecognizer types.PatternRecognizer
	json.Unmarshal([]byte(value), &newRecognizer)

	if isUpdate == false {
		// Insert new item, verify doesn't exists and append
		for _, element := range existingRecognizersArr {
			if element.Name == newRecognizer.Name {
				return errors.New(
					"custom pattern recognizer with name '" +
						element.Name + "' already exists")
			}
		}

		// verified, append to result array
		existingRecognizersArr = append(existingRecognizersArr, newRecognizer)
	} else {
		// Update, find and update
		found := false
		for i, element := range existingRecognizersArr {
			if element.Name == newRecognizer.Name {
				found = true

				log.Info("Found recognizer to be updated")
				// remove the 'old' value
				existingRecognizersArr = append(existingRecognizersArr[:i],
					existingRecognizersArr[i+1:]...)
				// append the new one
				existingRecognizersArr = append(existingRecognizersArr,
					newRecognizer)
				break
			}
		}
		if found == false {
			return errors.New("custom pattern recognizer with name '" +
				newRecognizer.Name + "' was not found")
		}
	}

	recognizersBytes, _ := json.Marshal(existingRecognizersArr)
	return setValue(recognizersBytes)
}

//applyGet returns a single recognizer
func applyGet(r *types.RecognizerGetRequest) (*types.RecognizersGetResponse, error) {
	existingItems, err := recognizersStore.Get(recognizersKey)
	if err != nil {
		log.Error(err.Error())
		return nil, err
	}

	// Find wanted recognizer
	if existingItems != "" {
		var recognizers []types.PatternRecognizer
		err = json.Unmarshal([]byte(existingItems), &recognizers)
		if err != nil {
			return nil, err
		}

		for _, element := range recognizers {
			if element.Name == r.Name {
				var res []*types.PatternRecognizer
				res = append(res, &element)
				return &types.RecognizersGetResponse{Recognizers: res}, nil
			}
		}
	}

	// Failed to find wanted recognizer
	return nil, errors.New("recognizer with name " + r.Name + " was not found")
}

//applyGetAll returns all the stored recognizers
func applyGetAll(r *types.RecognizersGetAllRequest) (*types.RecognizersGetResponse, error) {

	if recognizersStore == nil {
		return nil, errors.New("cache is missing")
	}

	log.Info("Loading recognizers from underlying storage")
	itemsStr, err := recognizersStore.Get(recognizersKey)

	if err != nil {
		return nil, err
	}

	if err == nil && itemsStr != "" {
		var items []types.PatternRecognizer
		var res []*types.PatternRecognizer
		byteItems := []byte(itemsStr)
		json.Unmarshal(byteItems, &items)
		for i := range items {
			res = append(res, &items[i])
		}

		result := &types.RecognizersGetResponse{Recognizers: res}
		log.Info("Returning %d recognizers", len(res))
		return result, nil
	} else if err == nil {
		log.Info("No recognizers were found")
		return &types.RecognizersGetResponse{}, nil
	}

	return nil, err
}

//applyInsertOrUpdate inserts or updates a recognizer in the store
func applyInsertOrUpdate(r *types.RecognizerInsertOrUpdateRequest, isUpdate bool) (*types.RecognizersStoreResponse, error) {

	itemBytes, err := json.Marshal(r.Value)
	if err != nil {
		return nil, err
	}

	err = insertOrUpdateRecognizer(string(itemBytes), isUpdate)
	return &types.RecognizersStoreResponse{}, err
}

//applyDelete deletes a recognizer
func applyDelete(r *types.RecognizerDeleteRequest) (*types.RecognizersStoreResponse, error) {
	if recognizersStore == nil {
		return nil,
			errors.New("cache is missing")
	}

	// When updating the underlying storage we want to ensure mutual
	// exclusivness. To avoid situtation of two concurrent updates that creates
	// a race condition. Resulting in a custom recognizer data loss
	writersLock()
	defer writersUnlock()
	existingRecognizersArr, err := getExistingRecognizers()
	if err != nil {
		return nil, err
	}

	found := false
	for i, element := range existingRecognizersArr {
		if element.Name == r.Name {
			log.Info("Found recognizer '" + r.Name + "'. Deleting")
			found = true
			existingRecognizersArr = append(existingRecognizersArr[:i],
				existingRecognizersArr[i+1:]...)
		}
	}
	if found == false {
		notFoundErrMsg := "Failed to find recognizer '" + r.Name + "'"
		log.Error(notFoundErrMsg)
		return nil, errors.New(notFoundErrMsg)
	}

	recognizersBytes, _ := json.Marshal(existingRecognizersArr)
	return &types.RecognizersStoreResponse{}, setValue(recognizersBytes)
}

//applyGetHash returns the hash of the stored recognizers
func applyGetHash() (*types.RecognizerHashResponse, error) {
	if recognizersStore == nil {
		return nil, errors.New("cache is missing")
	}

	hash, err := recognizersStore.Get(hashKey)
	if err != nil {
		errMsg := "Failed to find the latest hash"
		log.Error(errMsg)
		return nil, errors.New(errMsg)
	}

	// no error, however hash was not found, this means the redis is still
	// empty.
	if hash == "" {
		return &types.RecognizerHashResponse{}, nil
	}

	return &types.RecognizerHashResponse{RecognizersHash: hash}, nil
}

// Server methods

func (s *server) ApplyGet(ctx context.Context, r *types.RecognizerGetRequest) (*types.RecognizersGetResponse, error) {
	response, err := applyGet(r)
	if err != nil {
		log.Error(err.Error())
		return &types.RecognizersGetResponse{}, err
	}

	return response, nil
}

func (s *server) ApplyGetAll(ctx context.Context, r *types.RecognizersGetAllRequest) (*types.RecognizersGetResponse, error) {
	response, err := applyGetAll(r)
	if err != nil {
		log.Error(err.Error())
		return &types.RecognizersGetResponse{}, err
	}

	return response, nil
}

func (s *server) ApplyInsert(ctx context.Context, r *types.RecognizerInsertOrUpdateRequest) (*types.RecognizersStoreResponse, error) {
	response, err := applyInsertOrUpdate(r, false)
	if err != nil {
		log.Error(err.Error())
		return &types.RecognizersStoreResponse{}, err
	}

	return response, nil
}

func (s *server) ApplyUpdate(ctx context.Context, r *types.RecognizerInsertOrUpdateRequest) (*types.RecognizersStoreResponse, error) {
	response, err := applyInsertOrUpdate(r, true)
	if err != nil {
		log.Error(err.Error())
		return &types.RecognizersStoreResponse{}, err
	}

	return response, nil
}

func (s *server) ApplyDelete(ctx context.Context, r *types.RecognizerDeleteRequest) (*types.RecognizersStoreResponse, error) {
	response, err := applyDelete(r)
	if err != nil {
		log.Error(err.Error())
		return &types.RecognizersStoreResponse{}, err
	}

	return response, nil
}

func (s *server) ApplyGetHash(ctx context.Context,
	r *types.RecognizerGetHashRequest) (
	*types.RecognizerHashResponse, error) {
	response, err := applyGetHash()
	if err != nil {
		log.Error(err.Error())
		return &types.RecognizerHashResponse{}, err
	}

	return response, nil
}
