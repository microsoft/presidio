import os

from common.methods import image_redactor


def test_given_image_with_int_color_filling_then_we_get_redact_image():
    # gray redact
    expected_result_image = get_file("gray_redact.png")
    response = image_redactor("original_image.png", 255)
    validate_and_close(expected_result_image, response)


def test_given_image_with_tuple_color_filling_then_we_get_redact_image():
    # purple redact
    expected_result_image = get_file("purple_redact.png")
    response = image_redactor("original_image.png", "102, 0, 102")
    validate_and_close(expected_result_image, response)


def test_given_image_with_no_color_filling_then_we_get_redact_image():
    # black redact
    expected_result_image = get_file("black_redact.png")
    response = image_redactor("original_image.png")
    validate_and_close(expected_result_image, response)


def test_given_no_image_then_we_fail():
    # black redact
    expected_response = '{"error": "Invalid parameter, please insert image data"}'
    response = image_redactor("")
    assert response.status_code == 422
    assert response.content.decode() == expected_response


def get_file(file_name: str):
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, "..", "resources", file_name)
    return open(file_path, "rb")


def validate_and_close(expected_result_image, response):
    assert response.status_code == 200
    assert response.content == expected_result_image.read()
    expected_result_image.close()
