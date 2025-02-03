from typing import Dict, List, Tuple, Union

from presidio_image_redactor.entities import ImageRecognizerResult


class BboxProcessor:
    """Common module for general bounding box operators."""

    @staticmethod
    def get_bboxes_from_ocr_results(
        ocr_results: Dict[str, List[Union[int, str]]],
    ) -> List[Dict[str, Union[int, float, str]]]:
        """Get bounding boxes on padded image for all detected words from ocr_results.

        :param ocr_results: Raw results from OCR.
        :return: Bounding box information per word.
        """
        bboxes = []
        for i in range(len(ocr_results["text"])):
            detected_text = ocr_results["text"][i]
            if detected_text:
                bbox = {
                    "left": ocr_results["left"][i],
                    "top": ocr_results["top"][i],
                    "width": ocr_results["width"][i],
                    "height": ocr_results["height"][i],
                    "conf": float(ocr_results["conf"][i]),
                    "label": detected_text,
                }
                bboxes.append(bbox)

        return bboxes

    @staticmethod
    def get_bboxes_from_analyzer_results(
        analyzer_results: List[ImageRecognizerResult],
    ) -> List[Dict[str, Union[str, float, int]]]:
        """Organize bounding box info from analyzer results.

        :param analyzer_results: Results from using ImageAnalyzerEngine.

        :return: Bounding box info organized.
        """
        bboxes = []
        for i in range(len(analyzer_results)):
            result = analyzer_results[i].to_dict()

            bbox_item = {
                "entity_type": result["entity_type"],
                "score": result["score"],
                "left": result["left"],
                "top": result["top"],
                "width": result["width"],
                "height": result["height"],
            }
            bboxes.append(bbox_item)

        return bboxes

    @staticmethod
    def remove_bbox_padding(
        analyzer_bboxes: List[Dict[str, Union[str, float, int]]],
        padding_width: int,
    ) -> List[Dict[str, int]]:
        """Remove added padding in bounding box coordinates.

        :param analyzer_bboxes: The bounding boxes from analyzer results.
        :param padding_width: Pixel width used for padding (0 if no padding).

        :return: Bounding box information per word.
        """
        if padding_width < 0:
            raise ValueError("Padding width must be a non-negative integer.")

        if len(analyzer_bboxes) > 0:
            # Get fields
            has_label = False
            has_entity_type = False
            try:
                _ = analyzer_bboxes[0]["label"]
                has_label = True
            except KeyError:
                has_label = False
            try:
                _ = analyzer_bboxes[0]["entity_type"]
                has_entity_type = True
            except KeyError:
                has_entity_type = False

            # Remove padding from all bounding boxes
            if has_label is True and has_entity_type is True:
                bboxes = [
                    {
                        "left": max(0, bbox["left"] - padding_width),
                        "top": max(0, bbox["top"] - padding_width),
                        "width": bbox["width"],
                        "height": bbox["height"],
                        "label": bbox["label"],
                        "entity_type": bbox["entity_type"],
                    }
                    for bbox in analyzer_bboxes
                ]
            elif has_label is True and has_entity_type is False:
                bboxes = [
                    {
                        "left": max(0, bbox["left"] - padding_width),
                        "top": max(0, bbox["top"] - padding_width),
                        "width": bbox["width"],
                        "height": bbox["height"],
                        "label": bbox["label"],
                    }
                    for bbox in analyzer_bboxes
                ]
            elif has_label is False and has_entity_type is True:
                bboxes = [
                    {
                        "left": max(0, bbox["left"] - padding_width),
                        "top": max(0, bbox["top"] - padding_width),
                        "width": bbox["width"],
                        "height": bbox["height"],
                        "entity_type": bbox["entity_type"],
                    }
                    for bbox in analyzer_bboxes
                ]
            elif has_label is False and has_entity_type is False:
                bboxes = [
                    {
                        "left": max(0, bbox["left"] - padding_width),
                        "top": max(0, bbox["top"] - padding_width),
                        "width": bbox["width"],
                        "height": bbox["height"],
                    }
                    for bbox in analyzer_bboxes
                ]
        else:
            bboxes = analyzer_bboxes

        return bboxes

    @staticmethod
    def match_with_source(
        all_pos: List[Dict[str, Union[str, int, float]]],
        pii_source_dict: List[Dict[str, Union[str, int, float]]],
        detected_pii: Dict[str, Union[str, float, int]],
        tolerance: int = 50,
    ) -> Tuple[List[Dict[str, Union[str, int, float]]], bool]:
        """Match returned redacted PII bbox data with some source of truth for PII.

        :param all_pos: Dictionary storing all positives.
        :param pii_source_dict: List of PII labels for this instance.
        :param detected_pii: Detected PII (single entity from analyzer_results).
        :param tolerance: Tolerance for exact coordinates and size data.
        :return: List of all positive with PII mapped back as possible
        and whether a match was found.
        """
        all_pos_match = all_pos.copy()

        # Get info from detected PII (positive)
        results_left = detected_pii["left"]
        results_top = detected_pii["top"]
        results_width = detected_pii["width"]
        results_height = detected_pii["height"]
        try:
            results_score = detected_pii["score"]
        except KeyError:
            # Handle matching when no score available
            results_score = 0
        match_found = False

        # See what in the ground truth this positive matches
        for label in pii_source_dict:
            source_left = label["left"]
            source_top = label["top"]
            source_width = label["width"]
            source_height = label["height"]

            match_left = abs(source_left - results_left) <= tolerance
            match_top = abs(source_top - results_top) <= tolerance
            match_width = abs(source_width - results_width) <= tolerance
            match_height = abs(source_height - results_height) <= tolerance
            matching = [match_left, match_top, match_width, match_height]

            if False not in matching:
                # If match is found, carry over ground truth info
                positive = label
                positive["score"] = results_score
                all_pos_match.append(positive)
                match_found = True

        return all_pos_match, match_found
