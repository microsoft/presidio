# Swagger

This folder includes the docs needed to generate Swagger files for this API.

## API Spec

Presidio API spec is outlined in a yaml file [swagger.yaml](swagger.yaml).
You can view the Swagger yaml in a user friendly online editor.

To do this copy the contents of the `swagger.yaml` file, and paste them in the [Swagger Editor](http://editor.swagger.io/).

## Prerequisits

Make sure you have installed the following:

- [go](https://golang.org/)
- [go-swagger](https://goswagger.io/)

## Generate Swagger

Run the following command in this folder:

```
make swagger
```

This will re-generate the `swagger.yaml` file.
