import pytesseract


class OCR:
    """OCR class that performs OCR on a given image."""

    def perform_ocr(self, image: object) -> dict:
        """Perform OCR on a given image.

        :param image: PIL Image/numpy array or file path(str) to be processed

        :return: results dictionary containing bboxes and text for each detected word
        """
        output_type = pytesseract.Output.DICT
        return pytesseract.image_to_data(image, output_type=output_type)

    @staticmethod
    def get_text_from_ocr_dict(ocr_result: dict, separator: str = " ") -> str:
        """Combine the text from the OCR dict to full text.

        :param ocr_result: dictionary containing the ocr results per word
        :param separator: separator to use when joining the words

        return: str containing the full extracted text as string
        """
        if not ocr_result:
            return ""
        else:
            return separator.join(ocr_result["text"])
