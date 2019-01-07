package ocr

import (
	"encoding/xml"
	"strconv"
	"strings"

	"github.com/otiai10/gosseract"

	types "github.com/Microsoft/presidio-genproto/golang"
	log "github.com/Microsoft/presidio/pkg/logger"
)

//HOCR document
type document struct {
	Elements []element `xml:"div>p>span>span"`
}

//element in hocr xml
type element struct {
	Lang      string `xml:"lang,attr"`
	Direction string `xml:"dir,attr"`
	Title     string `xml:"title,attr"`
	ID        string `xml:"id,attr"`
	Class     string `xml:"class,attr"`
	Content   string `xml:",innerxml"`
}

//PerformOCR and return hocr output
func PerformOCR(image *types.Image) (*types.Image, error) {

	// Setup tesseract client
	client := gosseract.NewClient()
	defer client.Close()

	err := client.SetImageFromBytes(image.Data)
	if err != nil {
		return nil, err
	}

	out, err := client.HOCRText()
	if err != nil {
		return nil, err
	}

	log.Debug(out)

	doc, err := convertHOcrToElements(out)
	if err != nil {
		return nil, err
	}

	ocrImage := convertElementsToLocations(doc)

	return ocrImage, nil
}

func convertHOcrToElements(hocr string) (document, error) {
	var doc document
	header := `<?xml version="1.0" encoding="UTF-8"?>` + "\n"
	err := xml.Unmarshal(([]byte)(header+hocr), &doc)
	if err != nil {
		return document{}, err
	}
	return doc, nil
}

func convertElementsToLocations(doc document) *types.Image {

	currentLocation := 0

	image := &types.Image{
		Boundingboxes: make([]*types.Boundingbox, len(doc.Elements)),
	}

	for i, element := range doc.Elements {
		content := element.Content
		content = strings.Replace(content, "<strong><em>", "", -1)
		content = strings.Replace(content, "</em></strong>", "", -1)

		image.Text += content + " "
		length := len([]rune(content))
		bBox := strings.Split(element.Title, " ")

		xlocation, err := strconv.ParseFloat(bBox[1], 32)
		if err != nil {
			log.Warn("Error parsing xlocation:", err.Error())
		}

		width, err := strconv.ParseFloat(bBox[3], 32)
		if err != nil {
			log.Warn("Error parsing width:", err.Error())
		}

		ylocation, err := strconv.ParseFloat(bBox[2], 32)
		if err != nil {
			log.Warn("Error parsing ylocation:", err.Error())
		}

		height, err := strconv.ParseFloat(strings.TrimRight(bBox[4], ";"), 32)
		if err != nil {
			log.Warn("Error parsing height:", err.Error())
		}

		image.Boundingboxes[i] = &types.Boundingbox{
			XLocation:     (float32)(xlocation),
			Width:         (float32)(width),
			YLocation:     (float32)(ylocation),
			Height:        (float32)(height),
			Text:          content,
			StartPosition: (int32)(currentLocation),
			EndPosition:   (int32)(currentLocation + length),
		}
		currentLocation += length + 1
	}

	return image

}
