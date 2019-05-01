package main

import (
	"os"

	"github.com/stretchr/testify/assert"

	types "github.com/Microsoft/presidio-genproto/golang"
	"github.com/Microsoft/presidio/pkg/cache/mock"
	"github.com/Microsoft/presidio/pkg/platform"

	"testing"
)

// createNewRecognizer creates a single dummy recognizer with a given name
func createNewRecognizer(name string) types.PatternRecognizer {
	p := &types.Pattern{}
	p.Score = 0.123
	p.Regex = "*FindMe*"
	p.Name = "findme"
	patternArr := []*types.Pattern{}
	patternArr = append(patternArr, p)

	newRecognizer := types.PatternRecognizer{
		Name:     name,
		Patterns: patternArr,
		Entity:   "DEMO_ITEMS",
		Language: "en"}

	return newRecognizer
}

func TestMain(m *testing.M) {
	os.Setenv("REDIS_URL", "fake_redis")
	settings = platform.GetSettings()
	os.Exit(m.Run())
}

// Insert and Get, verify it worked
func TestInsertAndGetRecognizer(t *testing.T) {
	// Mock the store with a fake redis
	recognizersStore = mock.New()

	// Insert a new pattern recognizer
	newRecognizer := createNewRecognizer("DemoRecognizer1")
	r := &types.RecognizerInsertOrUpdateRequest{}
	r.Value = &newRecognizer
	_, err := applyInsertOrUpdate(r, false)
	assert.NoError(t, err)

	// Verify returned object is as expected
	getRequest := &types.RecognizerGetRequest{Name: newRecognizer.Name}
	getResponse, err := applyGet(getRequest)
	assert.NoError(t, err)
	assert.Equal(t, len(getResponse.Recognizers), 1)

	// Verify that the item is exactly as expected
	assert.Equal(t, &newRecognizer, getResponse.Recognizers[0])
}

// Try to update a non-existing item and expect to fail
func TestUpdateOfNonExisting(t *testing.T) {
	// Mock the store with a fake redis
	recognizersStore = mock.New()

	r := &types.RecognizerInsertOrUpdateRequest{}
	// Try to update, expect to fail as this item does not exists
	_, err := applyInsertOrUpdate(r, true)
	assert.Error(t, err)
}

// Try to insert the same item again and expect to fail (on the second time)
func TestConflictingInserts(t *testing.T) {
	// Mock the store with a fake redis
	recognizersStore = mock.New()

	// Store is empty...
	rawValues, err := recognizersStore.Get(recognizersKey)
	assert.NoError(t, err)
	assert.Equal(t, rawValues, "")

	// Insert a new pattern recognizer
	recognizer1 := createNewRecognizer("DemoRecognizer1")
	r := &types.RecognizerInsertOrUpdateRequest{}
	r.Value = &recognizer1
	// Insert, should be fine...
	_, err = applyInsertOrUpdate(r, false)
	assert.NoError(t, err)
	// This should fail as it already exists
	_, err = applyInsertOrUpdate(r, false)
	assert.Error(t, err)

	// Verify just one item was returned (even though we got an error, make sure
	// that indeed just one item is returned)
	getRequest := &types.RecognizersGetAllRequest{}
	getResponse, err := applyGetAll(getRequest)
	assert.NoError(t, err)
	assert.Equal(t, len(getResponse.Recognizers), 1)
}

// Try to insert several different items and expect to succeed
func TestMultipleDifferentInserts(t *testing.T) {
	// Mock the store with a fake redis
	recognizersStore = mock.New()

	// Store is empty...
	rawValues, err := recognizersStore.Get(recognizersKey)
	assert.NoError(t, err)
	assert.Equal(t, rawValues, "")

	// Insert a new pattern recognizer
	recognizer1 := createNewRecognizer("DemoRecognizer1")
	r := &types.RecognizerInsertOrUpdateRequest{}
	r.Value = &recognizer1
	_, err = applyInsertOrUpdate(r, false)
	assert.NoError(t, err)

	recognizer2 := createNewRecognizer("DemoRecognizer2")
	r = &types.RecognizerInsertOrUpdateRequest{}
	r.Value = &recognizer2
	_, err = applyInsertOrUpdate(r, false)
	assert.NoError(t, err)

	// Verify returned object is as expected
	getRequest := &types.RecognizersGetAllRequest{}
	getResponse, err := applyGetAll(getRequest)
	assert.NoError(t, err)
	assert.Equal(t, len(getResponse.Recognizers), 2)
}

// Delete the only existing item and expect to succeed
func TestDeleteOnlyRecognizer(t *testing.T) {
	// Mock the store with a fake redis
	recognizersStore = mock.New()

	// Store is empty...
	rawValues, err := recognizersStore.Get(recognizersKey)
	assert.NoError(t, err)
	assert.Equal(t, rawValues, "")

	// Insert a new pattern recognizer
	recognizer1 := createNewRecognizer("DemoRecognizer1")
	r := &types.RecognizerInsertOrUpdateRequest{}
	r.Value = &recognizer1
	_, err = applyInsertOrUpdate(r, false)
	assert.NoError(t, err)

	// Delete
	deleteRequest := &types.RecognizerDeleteRequest{Name: recognizer1.Name}
	_, err = applyDelete(deleteRequest)
	assert.NoError(t, err)

	// Get should fail as it was already deleted
	getRequest := &types.RecognizerGetRequest{Name: recognizer1.Name}
	_, err = applyGet(getRequest)
	assert.Error(t, err)

	getAllRequest := &types.RecognizersGetAllRequest{}
	res, err := applyGetAll(getAllRequest)
	assert.NoError(t, err)
	assert.Equal(t, len(res.Recognizers), 0)
}

func TestDeleteRecognizer(t *testing.T) {
	// Mock the store with a fake redis
	recognizersStore = mock.New()

	// Store is empty...
	rawValues, err := recognizersStore.Get(recognizersKey)
	assert.NoError(t, err)
	assert.Equal(t, rawValues, "")

	// Insert a new pattern recognizer
	recognizer1 := createNewRecognizer("DemoRecognizer1")
	r := &types.RecognizerInsertOrUpdateRequest{}
	r.Value = &recognizer1
	_, err = applyInsertOrUpdate(r, false)
	assert.NoError(t, err)

	// Insert a second item
	recognizer2 := createNewRecognizer("DemoRecognizer2")
	r = &types.RecognizerInsertOrUpdateRequest{}
	r.Value = &recognizer2
	_, err = applyInsertOrUpdate(r, false)
	assert.NoError(t, err)

	// Get should succeed with 2 values
	getRequest := &types.RecognizersGetAllRequest{}
	getResponse, err := applyGetAll(getRequest)
	assert.NoError(t, err)
	assert.Equal(t, len(getResponse.Recognizers), 2)

	// Delete
	deleteRequest := &types.RecognizerDeleteRequest{Name: "DemoRecognizer1"}
	_, err = applyDelete(deleteRequest)
	assert.NoError(t, err)

	// Get should succeed with just 1 value
	getRequest = &types.RecognizersGetAllRequest{}
	getResponse, err = applyGetAll(getRequest)
	assert.NoError(t, err)
	assert.Equal(t, len(getResponse.Recognizers), 1)
	assert.Equal(t, getResponse.Recognizers[0].Name, "DemoRecognizer2")
}

// Try to delete a non-existing item and expect to fail
func TestDeleteNonExistingRecognizer(t *testing.T) {
	// Mock the store with a fake redis
	recognizersStore = mock.New()

	// Store is empty...
	rawValues, err := recognizersStore.Get(recognizersKey)
	assert.NoError(t, err)
	assert.Equal(t, rawValues, "")

	// Delete
	deleteRequest := &types.RecognizerDeleteRequest{Name: "someName"}
	_, err = applyDelete(deleteRequest)
	assert.Error(t, err)
}

// Try to get the latest hash and fail as the store is empty
func TestHashDoesNotExists(t *testing.T) {
	// Mock the store with a fake redis
	recognizersStore = mock.New()

	// Store is empty...
	res, err := applyGetHash()
	assert.NoError(t, err)
	assert.Equal(t, res, &types.RecognizerHashResponse{})
}

// Try to get the latest hash
func TestGetHash(t *testing.T) {
	// Mock the store with a fake redis
	recognizersStore = mock.New()

	// Store is empty...
	res, err := applyGetHash()
	assert.NoError(t, err)
	assert.Equal(t, res, &types.RecognizerHashResponse{})

	// Now, insert an item
	// Insert a new pattern recognizer
	newRecognizer1 := createNewRecognizer("DemoRecognizer1")
	r := &types.RecognizerInsertOrUpdateRequest{}
	r.Value = &newRecognizer1
	_, err = applyInsertOrUpdate(r, false)
	assert.NoError(t, err)

	// Get hash again, it should succeed and value should not be empty
	res, err = applyGetHash()
	assert.NoError(t, err)
	assert.NotEqual(t, res, &types.RecognizerHashResponse{})

	// Now, update the store, get the hash again, make sure the hash
	// is not as the previous one --> was updated
	newRecognizer1.Language = "de"
	r.Value = &newRecognizer1
	_, err = applyInsertOrUpdate(r, true /* update */)
	assert.NoError(t, err)

	// Get hash again
	res2, err2 := applyGetHash()
	assert.NoError(t, err2)
	assert.NotEqual(t, res2, &types.RecognizerHashResponse{})
	// this and previous one are different
	assert.NotEqual(t, res.RecognizersHash, res2.RecognizersHash)
}
