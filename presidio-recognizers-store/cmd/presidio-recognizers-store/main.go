package main

import (
	"context"
	"encoding/json"
	"errors"
	"strconv"
	"time"

	"google.golang.org/grpc/reflection"

	"flag"

	"github.com/spf13/pflag"
	"github.com/spf13/viper"

	types "github.com/Microsoft/presidio-genproto/golang"

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
	timestampKey   = "custom_recognizers:last_update"
)

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

// setValue sets the recognizers array in the store and updates the last update
// timestamp
func setValue(value string, timestamp string) error {
	err := recognizersStore.Set(recognizersKey, value)
	if err != nil {
		log.Error(err.Error())
		return err
	}

	log.Info("Updating timestamp: " + timestamp)
	err = recognizersStore.Set(timestampKey, timestamp)
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
	currentTimeStr := strconv.FormatInt(time.Now().Unix(), 10)

	return setValue(string(recognizersBytes), currentTimeStr)
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
		log.Info("Preparing result to be returned")

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

	existingRecognizersArr, err := getExistingRecognizers()
	if err != nil {
		return nil, err
	}

	found := false
	for i, element := range existingRecognizersArr {
		if element.Name == r.Name {
			log.Info("Found it...")
			found = true
			existingRecognizersArr = append(existingRecognizersArr[:i],
				existingRecognizersArr[i+1:]...)
		}
	}
	if found == false {
		notFoundErrMsg := "Relevant item was not found"
		log.Error(notFoundErrMsg)
		return nil, errors.New(notFoundErrMsg)
	}

	recognizersBytes, _ := json.Marshal(existingRecognizersArr)
	currentTimeStr := strconv.FormatInt(time.Now().Unix(), 10)

	return &types.RecognizersStoreResponse{},
		setValue(string(recognizersBytes), currentTimeStr)
}

//applyGetTimestamp returns the latest timestamp (unix style), when the store
// was last updated on
func applyGetTimestamp() (*types.RecognizerTimestampResponse, error) {
	if recognizersStore == nil {
		return nil, errors.New("cache is missing")
	}

	timestamp, err := recognizersStore.Get(timestampKey)
	if err != nil || timestamp == "" {
		errMsg := "Failed to find the last update timestamp"
		log.Error(errMsg)
		return &types.RecognizerTimestampResponse{}, errors.New(errMsg)
	}

	timeInSeconds, _ := strconv.ParseUint(timestamp, 10, 64)
	return &types.RecognizerTimestampResponse{UnixTimestamp: timeInSeconds}, nil
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

func (s *server) ApplyGetTimestamp(ctx context.Context,
	r *types.RecognizerGetTimestampRequest) (
	*types.RecognizerTimestampResponse, error) {
	response, err := applyGetTimestamp()
	if err != nil {
		log.Error(err.Error())
		return &types.RecognizerTimestampResponse{}, err
	}

	return response, nil
}
