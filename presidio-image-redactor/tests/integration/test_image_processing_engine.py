import PIL
from PIL import Image
import numpy as np
import pytest
from methods import get_resource_image
from unittest import mock


from presidio_image_redactor import (
    ImagePreprocessor,
    ContrastSegmentedImageEnhancer,
    BilateralFilter,
    SegmentedAdaptiveThreshold,
    ImageRescaling,
)


def test_bilateral_filter_preprocess_image():
    # Create an instance of BilateralFilter
    bilateral_filter = BilateralFilter()

    # Create a dummy PIL image for testing
    image = PIL.Image.new("RGB", (100, 100))

    # Call preprocess_image method and check the returned values
    processed_image, metadata = bilateral_filter.preprocess_image(image)

    # Add assertions based on expected results
    assert isinstance(processed_image, PIL.Image.Image)
    assert isinstance(metadata, dict)
    assert "diameter" in metadata
    assert "sigma_color" in metadata
    assert "sigma_space" in metadata
    assert metadata["diameter"] == 3
    assert metadata["sigma_color"] == 40
    assert metadata["sigma_space"] == 40


low_contrast_image = 255 * np.ones((100, 100), dtype=np.uint8)
high_contrast_image = np.zeros((100, 100), dtype=np.uint8)
high_contrast_image[:50, :] = 255
adaptive_threshold_test_data = [
    (low_contrast_image, (10, 255, 0)),
    (high_contrast_image, (40, 0, 127.5)),
]


@pytest.mark.parametrize("image,expected", adaptive_threshold_test_data)
def test_segmented_adaptive_threshold_preprocess_image(image, expected):
    # Create an instance of SegmentedAdaptiveThreshold
    segmented_adaptive_threshold = SegmentedAdaptiveThreshold()

    # Call preprocess_image method and check the returned values
    processed_image, metadata = segmented_adaptive_threshold.preprocess_image(image)

    # Add assertions based on expected results
    assert isinstance(processed_image, PIL.Image.Image)
    assert isinstance(metadata, dict)
    assert "C" in metadata
    assert "background_color" in metadata
    assert "contrast" in metadata
    assert metadata["C"] == expected[0]
    assert metadata["background_color"] == expected[1]
    assert metadata["contrast"] == expected[2]


small_image = np.zeros((512, 512), dtype=np.uint8)
large_image = np.zeros((4096, 4096), dtype=np.uint8)
regular_image = np.zeros((1024, 1024), dtype=np.uint8)
rescaling_test_data = [
    (small_image, (2, (1024, 1024))),
    (large_image, (0.5, (2048, 2048))),
    (regular_image, (1, (1024, 1024))),
]


@pytest.mark.parametrize("image,expected", rescaling_test_data)
def test_segmented_image_rescaling_preprocess_image(image, expected):
    # Create an instance of SegmentedAdaptiveThreshold
    segmented_adaptive_threshold = ImageRescaling()

    # Call preprocess_image method and check the returned values
    processed_image, metadata = segmented_adaptive_threshold.preprocess_image(image)

    # Add assertions based on expected results
    assert isinstance(processed_image, PIL.Image.Image)
    assert isinstance(metadata, dict)
    assert "scale_factor" in metadata
    assert metadata["scale_factor"] == expected[0]
    assert np.array(processed_image).shape == expected[1]


def test_contrast_segmented_image_enhancer_preprocess_image():
    preprocessor = ContrastSegmentedImageEnhancer()
    image = get_resource_image("ocr_test.png")
    preprocessed_image, metadata = preprocessor.preprocess_image(image)
    assert isinstance(preprocessed_image, PIL.Image.Image)
    assert "scale_factor" in metadata


def test_contrast_segmented_image_enhancer__improve_contrast():
    preprocessor = ContrastSegmentedImageEnhancer()
    image = get_resource_image("ocr_test.png")
    result = preprocessor._improve_contrast(image)
    assert len(result) == 3
    assert isinstance(result[0], PIL.Image.Image)
    assert isinstance(result[1], np.float64)
    assert isinstance(result[2], np.float64)
    assert result[1] <= result[2]


def test_preprocess_image_with_pil_image():
    # Create a mock PIL image
    pil_image = Image.new("RGB", (256, 256))

    with mock.patch(
        "presidio_image_redactor.ImagePreprocessor.convert_image_to_array",
        side_effect=Exception("Skip the rest"),
    ) as mocked_function:
        with pytest.raises(Exception, match="Skip the rest"):
            SegmentedAdaptiveThreshold().preprocess_image(pil_image)

        # Assert 'convert_image_to_array' was called
        mocked_function.assert_called_once()


def test_preprocess_image_with_ndarray():
    # Create a mock numpy array
    array_image = np.zeros((512, 512), dtype=np.uint8)

    with mock.patch(
        "presidio_image_redactor.ImagePreprocessor.convert_image_to_array"
    ) as mocked_function:
        SegmentedAdaptiveThreshold().preprocess_image(array_image)

        # Assert 'convert_image_to_array' was not called
        mocked_function.assert_not_called()
