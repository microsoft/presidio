from copy import deepcopy
import tempfile
import PIL
from PIL import Image
import pydicom

from presidio_image_redactor import (
    OCR,
    TesseractOCR,
    ImageAnalyzerEngine,
    DicomImageRedactorEngine,
)
from presidio_image_redactor.image_pii_verify_engine import ImagePiiVerifyEngine
from presidio_analyzer import PatternRecognizer

from typing import Tuple, List, Optional


class DicomImagePiiVerifyEngine(ImagePiiVerifyEngine, DicomImageRedactorEngine):
    """Class to handle verification and evaluation for DICOM de-identification."""

    def __init__(
        self,
        ocr_engine: Optional[OCR] = None,
        image_analyzer_engine: Optional[ImageAnalyzerEngine] = None,
    ):
        """Initialize DicomImagePiiVerifyEngine object.

        :param ocr_engine: OCR engine to use.
        :param image_analyzer_engine: Image analyzer engine to use.
        """
        # Initialize OCR engine
        if not ocr_engine:
            self.ocr_engine = TesseractOCR()
        else:
            self.ocr_engine = ocr_engine

        # Initialize image analyzer engine
        if not image_analyzer_engine:
            self.image_analyzer_engine = ImageAnalyzerEngine()
        else:
            self.image_analyzer_engine = image_analyzer_engine

    def verify_dicom_instance(
        self,
        instance: pydicom.dataset.FileDataset,
        padding_width: int = 25,
        ocr_threshold: float = -1,
        **kwargs,
    ) -> Tuple[PIL.Image.Image, dict, list]:
        """Verify PII on a single DICOM instance.

        :param instance: Loaded DICOM instance including pixel data and metadata.
        :param padding_width: Padding width to use when running OCR.
        :param ocr_threshold: OCR threshold value between -1 and 100.
        :param kwargs: Additional values for the analyze method in ImageAnalyzerEngine.
        :return: DICOM instance with boxes identifying PHI, OCR results,
        and analyzer results.
        """
        instance_copy = deepcopy(instance)

        # Load image for processing
        with tempfile.TemporaryDirectory() as tmpdirname:
            # Convert DICOM to PNG and add padding for OCR (during analysis)
            is_greyscale = self._check_if_greyscale(instance_copy)
            image = self._rescale_dcm_pixel_array(instance_copy, is_greyscale)
            self._save_pixel_array_as_png(image, is_greyscale, "tmp_dcm", tmpdirname)

            png_filepath = f"{tmpdirname}/tmp_dcm.png"
            loaded_image = Image.open(png_filepath)
            image = self._add_padding(loaded_image, is_greyscale, padding_width)

        # Create custom recognizer using DICOM metadata
        original_metadata, is_name, is_patient = self._get_text_metadata(instance_copy)
        phi_list = self._make_phi_list(original_metadata, is_name, is_patient)
        deny_list_recognizer = PatternRecognizer(
            supported_entity="PERSON", deny_list=phi_list
        )
        ocr_results = self.ocr_engine.perform_ocr(image)
        analyzer_results = self.image_analyzer_engine.analyze(
            image,
            ad_hoc_recognizers=[deny_list_recognizer],
            ocr_threshold=ocr_threshold,
            **kwargs,
        )

        # Get image with verification boxes
        verify_image = self.verify(
            image, ad_hoc_recognizers=[deny_list_recognizer], **kwargs
        )

        return verify_image, ocr_results, analyzer_results

    def eval_dicom_instance(
        self,
        instance: pydicom.dataset.FileDataset,
        ground_truth: dict,
        padding_width: int = 25,
        tolerance: int = 50,
        ocr_threshold: float = -1,
        **kwargs,
    ) -> Tuple[PIL.Image.Image, dict]:
        """Evaluate performance for a single DICOM instance.

        :param instance: Loaded DICOM instance including pixel data and metadata.
        :param ground_truth: Dictionary containing ground truth labels for the instance.
        :param padding_width: Padding width to use when running OCR.
        :param tolerance: Pixel distance tolerance for matching to ground truth.
        :param ocr_threshold: OCR threshold value between -1 and 100.
        :param kwargs: Additional values for the analyze method in ImageAnalyzerEngine.
        :return: Evaluation comparing redactor engine results vs ground truth.
        """
        # Verify detected PHI
        verify_image, ocr_results, analyzer_results = self.verify_dicom_instance(
            instance, padding_width, ocr_threshold, **kwargs
        )
        formatted_ocr_results = self._get_bboxes_from_ocr_results(ocr_results)
        detected_phi = self._get_bboxes_from_analyzer_results(analyzer_results)

        # Remove duplicate entities in results
        detected_phi = self._remove_duplicate_entities(detected_phi)

        # Get correct PHI text (all TP and FP)
        all_pos = self._label_all_positives(
            ground_truth, formatted_ocr_results, detected_phi, tolerance
        )

        # Calculate evaluation metrics
        precision = self.calculate_precision(ground_truth, all_pos)
        recall = self.calculate_recall(ground_truth, all_pos)

        eval_results = {
            "all_positives": all_pos,
            "ground_truth": ground_truth,
            "precision": precision,
            "recall": recall,
        }

        return verify_image, eval_results

    @staticmethod
    def _get_bboxes_from_ocr_results(ocr_results: dict) -> List[dict]:
        """Get bounding boxes on padded image for all detected words from ocr_results.

        :param ocr_results: Raw results from OCR.
        :return: Bounding box information per word.
        """
        bboxes = []
        item_count = 0
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
                item_count += 1

        return bboxes

    @staticmethod
    def _remove_duplicate_entities(
        results: List[dict], dup_pix_tolerance: int = 5
    ) -> List[dict]:
        """Handle when a word is detected multiple times as different types of entities.

        :param results: List of detected PHI with bbox info.
        :param dup_pix_tolerance: Pixel difference tolerance for identifying duplicates.
        :return: Detected PHI with no duplicate entities.
        """
        dups = []
        results_no_dups = results.copy()
        dims = ["left", "top", "width", "height"]

        # Check for duplicates
        for i in range(len(results) - 1):
            i_dims = {dim: results[i][dim] for dim in dims}

            # Ignore if we've already detected this dup combination
            for other in range(i + 1, len(results)):
                if i not in dups:
                    other_dims = {dim: results[other][dim] for dim in dims}
                    matching_dims = {
                        dim: abs(i_dims[dim] - other_dims[dim]) <= dup_pix_tolerance
                        for dim in dims
                    }
                    matching = list(matching_dims.values())

                    if all(matching):
                        dups.append(other)

        # Remove duplicates
        for dup_index in sorted(dups, reverse=True):
            del results_no_dups[dup_index]

        return results_no_dups

    @staticmethod
    def _match_with_source(
        all_pos: List[dict],
        phi_source_dict: List[dict],
        detected_phi: dict,
        tolerance: int = 50,
    ) -> Tuple[dict, bool]:
        """Match returned redacted PHI bbox data with some source of truth for PHI.

        :param all_pos: Dictionary storing all positives.
        :param phi_source_dict: List of PHI labels for this instance.
        :param detected_phi: Detected PHI (single entity from analyzer_results).
        :param tolerance: Tolerance for exact coordinates and size data.
        :return: List of all positive with PHI mapped back as possible
        and whether a match was found.
        """
        # Get info from detected PHI (positive)
        results_left = detected_phi["left"]
        results_top = detected_phi["top"]
        results_width = detected_phi["width"]
        results_height = detected_phi["height"]
        results_score = detected_phi["score"]
        match_found = False

        # See what in the ground truth this positive matches
        for label in phi_source_dict:
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
                all_pos.append(positive)
                match_found = True

        return all_pos, match_found

    @classmethod
    def _label_all_positives(
        cls,
        gt_labels_dict: dict,
        ocr_results: List[dict],
        detected_phi: List[dict],
        tolerance: int = 50,
    ) -> List[dict]:
        """Label all entities detected as PHI by using ground truth and OCR results.

        All positives (detected_phi) do not contain PHI labels and are thus
        difficult to work with intuitively. This method maps back to the
        actual PHI to each detected sensitive entity.

        :param gt_labels_dict: Dictionary with ground truth labels for a
        single DICOM instance.
        :param ocr_results: All detected text.
        :param detected_phi: Formatted analyzer_results.
        :param tolerance: Tolerance for exact coordinates and size data.
        :return: List of all positives, labeled.
        """
        all_pos = []

        # Cycle through each positive (TP or FP)
        for analyzer_result in detected_phi:

            # See if there are any ground truth matches
            all_pos, gt_match_found = cls._match_with_source(
                all_pos, gt_labels_dict, analyzer_result, tolerance
            )

            # If not, check back with OCR
            if not gt_match_found:
                all_pos, _ = cls._match_with_source(
                    all_pos, ocr_results, analyzer_result, tolerance
                )

        # Remove any duplicates
        all_pos = cls._remove_duplicate_entities(all_pos, 0)

        return all_pos

    @staticmethod
    def calculate_precision(gt: List[dict], all_pos: List[dict]) -> float:
        """Calculate precision.

        :param gt: List of ground truth labels.
        :param all_pos: All Detected PHI (mapped back to have actual PHI text).
        :return: Precision value.
        """
        # Find True Positive (TP) and precision
        tp = [i for i in all_pos if i in gt]
        try:
            precision = len(tp) / len(all_pos)
        except ZeroDivisionError:
            precision = 0

        return precision

    @staticmethod
    def calculate_recall(gt: List[dict], all_pos: List[dict]) -> float:
        """Calculate recall.

        :param gt: List of ground truth labels.
        :param all_pos: All Detected PHI (mapped back to have actual PHI text).
        :return: Recall value.
        """
        # Find True Positive (TP) and precision
        tp = [i for i in all_pos if i in gt]
        try:
            recall = len(tp) / len(gt)
        except ZeroDivisionError:
            recall = 1

        return recall
