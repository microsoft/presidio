package templates

import (
	"fmt"

	types "github.com/Microsoft/presidio-genproto/golang"
	"github.com/Microsoft/presidio/pkg/presidio"
	store "github.com/Microsoft/presidio/presidio-api/cmd/presidio-api/api"
)

//GetFieldTypes get all available field types
func GetFieldTypes() []types.FieldTypes {
	var fieldTypeArray []types.FieldTypes
	for key := range types.FieldTypesEnum_value {
		fieldTypeArray = append(fieldTypeArray, types.FieldTypes{Name: key})
	}
	return fieldTypeArray
}

//GetActionTemplate get template for different actions
func GetActionTemplate(api *store.API, project, action, id string) (string, error) {
	return api.Templates.GetTemplate(project, action, id)
}

//PostActionTemplate insert template for different actions
func PostActionTemplate(api *store.API, project, action, id, value string) (string, error) {
	err := api.Templates.InsertTemplate(project, action, id, value)
	if err != nil {
		return "", err
	}
	return "Template added successfully", nil
}

//PutActionTemplate update template
func PutActionTemplate(api *store.API, project, action, id, value string) (string, error) {
	err := api.Templates.UpdateTemplate(project, action, id, value)
	if err != nil {
		return "", err
	}

	return "Template updated successfully", nil
}

//DeleteActionTemplate delete template
func DeleteActionTemplate(api *store.API, project, action, id string) (string, error) {
	err := api.Templates.DeleteTemplate(project, action, id)
	if err != nil {
		return "", err
	}
	return "Template deleted successfully", err
}

//GetTemplate based on id or json(tmpl)
func GetTemplate(api *store.API, project, action, id string, obj interface{}) error {

	if id == "" {
		return nil
	}

	template, err := api.Templates.GetTemplate(project, action, id)
	if err != nil {
		return err
	}

	err = presidio.ConvertJSONToInterface(template, obj)
	if err != nil {
		return err
	}
	if obj == nil {
		return fmt.Errorf("%s template is empty", action)
	}
	return nil
}
