import os

from common.methods import image_redactor


def test_given_image_with_int_color_filling_then_we_get_redact_image():
    # black redact
    expected_result_image = get_file("black_redact.png")
    status, result_image = image_redactor("original_image.png", 0)
    assert result_image == expected_result_image.read()
    assert status == 200


def test_given_image_with_tuple_color_filling_then_we_get_redact_image():
    # purple redact
    expected_result_image = get_file("purple_redact.png")
    status, result_image = image_redactor("original_image.png", (102, 0, 102))
    assert result_image == expected_result_image.read()
    assert status == 200


def test_given_image_with_no_color_filling_then_we_get_redact_image():
    # purple redact
    expected_result_image = get_file("purple_redact.png")
    status, result_image = image_redactor("original_image.png")
    assert result_image == expected_result_image.read()
    assert status == 200


def compare_images(image_one, image_two):
    return image_one == image_two.read()


def get_file(file_name: str):
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, "..", "resources", file_name)
    return open(file_path, "rb")
