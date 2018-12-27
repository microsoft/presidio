package templates

import (
	"testing"

	"github.com/stretchr/testify/assert"

	cmock "github.com/Microsoft/presidio/pkg/cache/mock"
	"github.com/Microsoft/presidio/pkg/platform/kube"
)

func TestTemplatesWithCache(t *testing.T) {
	c := cmock.New()
	k, _ := kube.NewFake()
	tm := New(k, c)

	project := "p"
	action := "a"
	id := "i"
	value := "v"

	// Insert template
	err := tm.InsertTemplate(project, action, id, value)
	assert.NoError(t, err)

	// Get Template
	v, err := tm.GetTemplate(project, action, id)
	assert.NoError(t, err)
	assert.Equal(t, value, v)

	// Delete Template
	err = tm.DeleteTemplate(project, action, id)
	assert.NoError(t, err)

	// Verify template is deleted
	_, err = tm.GetTemplate(project, action, id)
	assert.Error(t, err)
}

func TestTemplatesWithoutCache(t *testing.T) {
	k, _ := kube.NewFake()
	tm := New(k, nil)

	project := "p"
	action := "a"
	id := "i"
	value := "v"

	// Insert template
	err := tm.InsertTemplate(project, action, id, value)
	assert.NoError(t, err)

	// Get Template
	v, err := tm.GetTemplate(project, action, id)
	assert.NoError(t, err)
	assert.Equal(t, value, v)

	// Delete Template
	err = tm.DeleteTemplate(project, action, id)
	assert.NoError(t, err)

	// Verify template is deleted
	_, err = tm.GetTemplate(project, action, id)
	assert.Error(t, err)
}
