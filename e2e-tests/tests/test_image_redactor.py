from common.methods import image_redactor


def test_image_redactor():
    status, result = image_redactor("image.png", 255)
    assert status == 200
    # curl - XPOST
    # "http://localhost:3000/anonymize" - H
    # "content-type: multipart/form-data" - F
    # "image=@ocr_test.png" - F
    # "data=\"{'color_fill':'255'}\"" > out.png
