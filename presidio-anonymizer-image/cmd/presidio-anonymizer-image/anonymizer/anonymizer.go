package anonymizer

import (
	"bytes"
	"fmt"
	img "image"
	"image/color"
	"strings"

	"github.com/disintegration/imaging"

	types "github.com/Microsoft/presidio-genproto/golang"
)

//AnonymizeImage text or just bounding boxes
func AnonymizeImage(image *types.Image, detectionType types.DetectionTypeEnum, results []*types.AnalyzeResult, template *types.AnonymizeImageTemplate) (*types.Image, error) {

	// Get format
	if image.ImageType == "" {
		return nil, fmt.Errorf("Image type is empty")
	}

	splitted := strings.Split(image.ImageType, "/")
	var f string
	if len(splitted) == 2 {
		f = splitted[1]
	} else {
		f = splitted[0]
	}

	format, err := imaging.FormatFromExtension(f)
	if err != nil {
		return nil, err
	}

	// Read byte slice
	r := bytes.NewReader(image.Data)
	decodedImage, err := imaging.Decode(r)

	if err != nil {
		return nil, err
	}

	// Redact text
	if detectionType == types.DetectionTypeEnum_OCR {
		decodedImage = redactText(decodedImage, image, results, template)
	} else {
		return nil, fmt.Errorf("Detection method not supported")
	}

	// Save image
	buf := new(bytes.Buffer)
	err = imaging.Encode(buf, decodedImage, format)
	if err != nil {
		return nil, err
	}

	return &types.Image{Data: buf.Bytes()}, nil
}

func redactText(dimg img.Image, image *types.Image, results []*types.AnalyzeResult, template *types.AnonymizeImageTemplate) img.Image {

	for _, result := range results {
		if result == nil {
			continue
		}

		location := result.Location

		for _, bbox := range image.Boundingboxes {

			for _, graphic := range template.FieldTypeGraphics {
				//All fields will be redacted
				if graphic.Fields == nil {
					dimg = fillBbox(dimg, bbox, location, graphic)
					break
				}
				//Specified fields will be redacted
				for _, fieldType := range graphic.Fields {
					if fieldType.Name == result.Field.Name {
						dimg = fillBbox(dimg, bbox, location, graphic)
						break
					}

				}
			}
		}
	}
	return dimg
}

func fillBbox(dimg img.Image, bbox *types.Boundingbox, location *types.Location, graphic *types.FieldTypeGraphic) img.Image {

	var col color.NRGBA
	if graphic.Graphic != nil && graphic.Graphic.FillColorValue != nil {
		col = color.NRGBA{
			(uint8)(graphic.Graphic.FillColorValue.Red),
			(uint8)(graphic.Graphic.FillColorValue.Green),
			(uint8)(graphic.Graphic.FillColorValue.Blue),
			255,
		}
	} else {
		col = color.NRGBA{0, 0, 0, 255} // Black
	}

	if (bbox.StartPosition >= location.Start && bbox.EndPosition <= location.End+1) || (location.Start >= bbox.StartPosition && location.End <= bbox.EndPosition) {
		x := int(bbox.XLocation)
		y := int(bbox.YLocation)
		w := int(bbox.Width)
		h := int(bbox.Height)

		dst := imaging.New(w-x, h-y, col)
		dimg = imaging.Paste(dimg, dst, img.Pt(x, y))
	}
	return dimg
}
