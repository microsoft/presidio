package main

import (
	"bytes"
	"flag"
	"io"
	"io/ioutil"
	"mime/multipart"
	"net/http"
	"net/url"
	"os"
	"strconv"
	"strings"

	log "github.com/Microsoft/presidio/pkg/logger"

	"github.com/Microsoft/presidio/pkg/platform"

	"github.com/spf13/pflag"
	"github.com/spf13/viper"
)

// APIEP api endpoint
var APIEP = ""

func main() {
	pflag.Int(platform.WebPort, 8080, "API Port")
	pflag.String(platform.APISvcAddress, "127.0.0.1", "Api Service Endpoint")
	pflag.String("log_level", "info", "Log level - debug/info/warn/error")

	pflag.CommandLine.AddGoFlagSet(flag.CommandLine)
	pflag.Parse()
	viper.BindPFlags(pflag.CommandLine)

	settings := platform.GetSettings()
	APIEP = settings.APISvcAddress + ":" + strconv.Itoa(settings.WebPort)

	log.Info("Starting e2e test")
	TestAddTemplate()
	TestDeleteTemplate()
	TestAnalyzer()
	TestAnonymizer()
	TestImageAnonymizer()
	log.Info("Ended e2e test")
}

func generatePayload(name string) []byte {
	payload, err := ioutil.ReadFile("./testdata/" + name)
	if err != nil {
		panic(err)
	}
	return payload
}

func invokeHTTPRequest(path string, method string, payload []byte) string {

	request := &http.Request{
		Method: method,
		URL:    &url.URL{Scheme: "http", Host: APIEP, Path: path},
		Body:   ioutil.NopCloser(bytes.NewReader(payload)),
		Header: http.Header{
			"Content-Type": []string{"application/json"},
		},
	}

	resp, err := http.DefaultClient.Do(request)
	if err != nil {
		panic(err)
	}
	if resp.StatusCode >= 300 {
		log.Error("%s %s: expected status code smaller than 300 , got '%d'\n", request.Method, request.URL.String(), resp.StatusCode)
		panic("Bad status code")
	}
	defer resp.Body.Close()
	bodyBytes, _ := ioutil.ReadAll(resp.Body)
	return string(bodyBytes)
}

func invokeHTTPUpload(path string, values map[string]io.Reader) []byte {

	var b bytes.Buffer
	w := multipart.NewWriter(&b)
	for key, r := range values {
		var fw io.Writer
		var err error
		if x, ok := r.(io.Closer); ok {
			defer x.Close()
		}
		// Add an image file
		if x, ok := r.(*os.File); ok {
			fw, err = w.CreateFormFile(key, x.Name())

		} else {
			// Add other fields
			fw, err = w.CreateFormField(key)
		}
		if err != nil {
			panic(err)
		}
		_, err = io.Copy(fw, r)
		if err != nil {
			panic(err)
		}
	}

	w.Close()

	req, err := http.NewRequest("POST", "http://"+APIEP+path, &b)
	if err != nil {
		panic(err)
	}
	req.Header.Set("Content-Type", w.FormDataContentType())

	res, err := http.DefaultClient.Do(req)
	if err != nil {
		panic(err)
	}
	if res.StatusCode != http.StatusOK {
		log.Error("bad status: %s", res.Status)
		panic("Bad status code")
	}
	defer res.Body.Close()
	bodyBytes, _ := ioutil.ReadAll(res.Body)
	return bodyBytes
}

// TestAddTemplate Test Add Template
func TestAddTemplate() {
	log.Info("Start TestAddTemplate")
	log.Info("Adding analyze template")
	payload := generatePayload("analyze-template.json")
	invokeHTTPRequest("/api/v1/templates/test/analyze/test", "POST", payload)

	log.Info("Adding anonymize template")
	payload = generatePayload("anonymize-template.json")
	invokeHTTPRequest("/api/v1/templates/test/anonymize/test", "POST", payload)
	log.Info("End TestAddTemplate")
}

//TestDeleteTemplate Test Delete Template
func TestDeleteTemplate() {
	log.Info("Start TestDeleteTemplate")
	log.Info("Delete analyze template")
	invokeHTTPRequest("/api/v1/templates/test/analyze/test", "DELETE", []byte(""))
	log.Info("Delete anonymize template")
	invokeHTTPRequest("/api/v1/templates/test/anonymize/test", "DELETE", []byte(""))
	log.Info("End TestDeleteTemplate")
}

//TestAnalyzer Test Analyzer
func TestAnalyzer() {
	log.Info("Start TestAnalyzer")
	TestAddTemplate()
	payload := generatePayload("analyze-request.json")
	log.Info("Analyze request")
	invokeHTTPRequest("/api/v1/projects/test/analyze", "POST", payload)
	log.Info("End TestAnalyzer")
}

//TestAnonymizer Test Anonymizer
func TestAnonymizer() {
	log.Info("Start TestAnonymizer")
	TestAddTemplate()
	payload := generatePayload("anonymize-request.json")
	log.Info("anonymize request")
	invokeHTTPRequest("/api/v1/projects/test/anonymize", "POST", payload)
	log.Info("End TestAnonymizer")
}

//TestImageAnonymizer Test Image Anonymizer
func TestImageAnonymizer() {
	log.Info("Start TestImageAnonymizer")
	file, err := os.Open("./testdata/ocr-test.png")
	if err != nil {
		panic(err)
	}
	payload := map[string]io.Reader{
		"file":                   file,
		"analyzeTemplate":        strings.NewReader((string)(generatePayload("analyze-image-template.json"))),
		"anonymizeImageTemplate": strings.NewReader((string)(generatePayload("anonymize-image-template.json"))),
		"imageType":              strings.NewReader("image/png"),
		"detectionType":          strings.NewReader("OCR"),
	}

	log.Info("Sending anonymize image request")
	result := invokeHTTPUpload("/api/v1/projects/test/anonymize-image", payload)
	savedOutputImage, err := ioutil.ReadFile("./testdata/ocr-result.png")
	if err != nil {
		panic(err)
	}
	if len(savedOutputImage) != len(result) {
		log.Error("Images are not equal")
		panic("Images are not equal")
	}
	log.Info("End TestImageAnonymizer")
}
