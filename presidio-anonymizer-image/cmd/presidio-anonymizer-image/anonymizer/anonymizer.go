package anonymizer

import (
	img "gopkg.in/gographics/imagick.v3/imagick"

	types "github.com/Microsoft/presidio-genproto/golang"
)

//AnonymizeImage text or just bounding boxes
func AnonymizeImage(image *types.Image, detectionType types.DetectionTypeEnum, results []*types.AnalyzeResult, template *types.AnonymizeImageTemplate) (*types.Image, error) {

	img.Initialize()
	defer img.Terminate()

	mw := img.NewMagickWand()
	defer mw.Destroy()
	mw.ReadImageBlob(image.Data)

	if detectionType == types.DetectionTypeEnum_OCR {
		redactText(mw, image, results, template)
	}

	newImage := mw.GetImageBlob()
	return &types.Image{Data: newImage}, nil
}

func redactText(mw *img.MagickWand, image *types.Image, results []*types.AnalyzeResult, template *types.AnonymizeImageTemplate) {

	for _, result := range results {
		if result == nil {
			continue
		}

		location := result.Location

		for _, bbox := range image.Boundingboxes {

			for _, graphic := range template.FieldTypeGraphics {
				if graphic.Fields == nil {
					fillBbox(mw, bbox, location, graphic)
					break
				}
				for _, fieldType := range graphic.Fields {
					if fieldType.Name == result.Field.Name {
						fillBbox(mw, bbox, location, graphic)
						break
					}

				}
			}
		}
	}
}

func fillBbox(mw *img.MagickWand, bbox *types.Boundingbox, location *types.Location, graphic *types.FieldTypeGraphic) {

	dw := img.NewDrawingWand()

	if graphic.Graphic != nil && graphic.Graphic.FillColorValue != nil {
		pw := img.NewPixelWand()
		pw.SetRed(graphic.Graphic.FillColorValue.Red)
		pw.SetGreen(graphic.Graphic.FillColorValue.Green)
		pw.SetBlue(graphic.Graphic.FillColorValue.Blue)
		dw.SetFillColor(pw)
	}

	if bbox.StartPosition >= location.Start && bbox.EndPosition <= location.End+1 {
		x := (float64)(bbox.XLocation)
		y := (float64)(bbox.YLocation)
		w := (float64)(bbox.Width)
		h := (float64)(bbox.Height)
		dw.Rectangle(x, y, w, h)
		mw.DrawImage(dw)
	}

}
