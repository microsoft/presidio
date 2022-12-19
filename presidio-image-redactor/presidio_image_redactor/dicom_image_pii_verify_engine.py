from copy import deepcopy
import tempfile
import PIL
from PIL import Image
import pydicom

from presidio_image_redactor import (
    TesseractOCR,
    ImageAnalyzerEngine,
    DicomImageRedactorEngine,
)
from presidio_image_redactor.image_pii_verify_engine import ImagePiiVerifyEngine
from presidio_analyzer import PatternRecognizer

from typing import Tuple, Optional


class DicomImagePiiVerifyEngine(ImagePiiVerifyEngine, DicomImageRedactorEngine):
    """Class to handle verification and evaluation for DICOM de-identification."""

    def __init__(
        self,
        ocr_engine: Optional[TesseractOCR] = None,
        image_analyzer_engine: Optional[ImageAnalyzerEngine] = None,
    ):
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
        **kwargs,
    ) -> Tuple[PIL.Image.Image, dict, dict]:
        """Verify PII on a single DICOM instance.

        :param instance: Loaded DICOM instance including pixel data and metadata.
        :param padding_width: Padding width to use when running OCR.
        :param kwargs: Additional values for the analyze method in ImageAnalyzerEngine.
        :return: DICOM instance with boxes identifying PHI, OCR results, and analyzer results.
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
            image, ad_hoc_recognizers=[deny_list_recognizer], **kwargs
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
        **kwargs,
    ) -> Tuple[PIL.Image.Image, dict]:
        """Evaluate performance for a single DICOM instance

        :param instance: Loaded DICOM instance including pixel data and metadata.
        :param ground_truth: Dictionary containing ground truth labels for the instance.
        :param padding_width: Padding width to use when running OCR.
        :param tolerance: Pixel distance tolerance for matching to ground truth.
        :param kwargs: Additional values for the analyze method in ImageAnalyzerEngine.
        :return: Evaluation comparing redactor engine results vs ground truth.
        """
        # Verify detected PHI
        verify_image, ocr_results, analyzer_results = self.verify_dicom_instance(
            instance, padding_width, **kwargs
        )
        formatted_ocr_results = self._get_bboxes_from_ocr_results(ocr_results)
        detected_PHI = self._get_bboxes_from_analyzer_results(analyzer_results)

        # Remove duplicate entities in results
        detected_PHI = self._remove_duplicate_entities(detected_PHI)

        # Get correct PHI text (all TP and FP)
        all_pos = self._label_all_positives(
            ground_truth, formatted_ocr_results, detected_PHI, tolerance
        )

        # Calculate evaluation metrics
        precision = self._calculate_precision(ground_truth, all_pos)
        recall = self._calculate_recall(ground_truth, all_pos)

        eval_results = {
            "all_positives": all_pos,
            "ground_truth": ground_truth,
            "precision": precision,
            "recall": recall,
        }

        return verify_image, eval_results

    @staticmethod
    def _get_bboxes_from_ocr_results(ocr_results: dict) -> dict:
        """Get bounding boxes on padded image for all detected words from ocr_results.

        Args:
            ocr_results (dict): Results from OCR.

        Return:
            bboxes (dict): Bounding box information per word.
        """
        bboxes = {}
        item_count = 0
        for i in range(0, len(ocr_results["text"])):
            detected_text = ocr_results["text"][i]
            if len(detected_text) > 0:
                bboxes[str(item_count)] = {
                    "left": ocr_results["left"][i],
                    "top": ocr_results["top"][i],
                    "width": ocr_results["width"][i],
                    "height": ocr_results["height"][i],
                    "conf": float(ocr_results["conf"][i]),
                    "label": detected_text,
                }
                item_count += 1

        return bboxes

    @staticmethod
    def _remove_duplicate_entities(results: dict, dup_pix_tolerance: int = 5) -> dict:
        """Remove duplication where the same word is detected multiple times as different types of entities.

        Args:
            results (dict): Detected PHI.
            dup_pix_tolerance (int): Pixel difference tolerance for identifying duplicates.

        Return:
            results_no_dups (dict): Detected PHI with no duplicate entities.
        """
        dups = []
        results_no_dups = results.copy()

        # Check for duplicates
        for i in results:
            i_left = results[i]["left"]
            i_top = results[i]["top"]
            i_width = results[i]["width"]
            i_height = results[i]["height"]

            # Ignore if we've already detected this dup combination
            for other in results:
                if i not in dups:
                    if i != other:
                        other_left = results[other]["left"]
                        other_top = results[other]["top"]
                        other_width = results[other]["width"]
                        other_height = results[other]["height"]

                        match_left = abs(i_left - other_left) <= dup_pix_tolerance
                        match_top = abs(i_top - other_top) <= dup_pix_tolerance
                        match_width = abs(i_width - other_width) <= dup_pix_tolerance
                        match_height = abs(i_height - other_height) <= dup_pix_tolerance
                        matching = [match_left, match_top, match_width, match_height]

                        if False not in matching:
                            dups.append(other)

        # Remove duplicates
        for dup in dups:
            results_no_dups.pop(dup)

        return results_no_dups

    @staticmethod
    def _match_with_source(
        all_pos: dict, PHI_source_dict: dict, detected_PHI: dict, tolerance: int = 50
    ) -> dict:
        """Match returned redacted PHI bbox data with some source of truth for PHI.

        Args:
            all_pos (dict): Dictionary storing all positives.
            PHI_source_dict (dict): Dictionary with PHI labels for this instance.
            detected_PHI (dict): Detected PHI (single entity from analyzer_results).
            tolerance (int): Tolerance for exact coordinates and size data.

        Return:
            all_pos (dict): Results dict with all positives, PHI mapped back as possible.
            match_found (bool): Whether a match was found.
        """
        # Get info from detected PHI (positive)
        results_left = detected_PHI["left"]
        results_top = detected_PHI["top"]
        results_width = detected_PHI["width"]
        results_height = detected_PHI["height"]
        results_score = detected_PHI["score"]
        match_found = False

        # See what in the ground truth this positive matches
        for label in PHI_source_dict:
            source_left = PHI_source_dict[label]["left"]
            source_top = PHI_source_dict[label]["top"]
            source_width = PHI_source_dict[label]["width"]
            source_height = PHI_source_dict[label]["height"]

            match_left = abs(source_left - results_left) <= tolerance
            match_top = abs(source_top - results_top) <= tolerance
            match_width = abs(source_width - results_width) <= tolerance
            match_height = abs(source_height - results_height) <= tolerance
            matching = [match_left, match_top, match_width, match_height]

            if False not in matching:
                # If match is found, carry over ground truth info
                all_pos[label] = PHI_source_dict[label]
                all_pos[label]["score"] = results_score
                match_found = True

        return all_pos, match_found

    @classmethod
    def _label_all_positives(
        cls,
        gt_labels_dict: dict,
        ocr_results: dict,
        analyzer_results: dict,
        tolerance: int = 50,
    ) -> dict:
        """Label all entities detected as PHI by using ground truth and OCR results.

        All positives (analyzer_results) do not contain PHI labels and are thus
        difficult to work with intuitively. This method maps back to the
        actual PHI to each detected sensitive entity.

        Args:
            gt_labels_dict (dict): Dictionary with ground truth labels for a single DICOM instance.
            ocr_results (dict): All detected text.
            analyzer_results (dict): Detected PHI.
            tolerance (int): Tolerance for exact coordinates and size data.

        Return:
            all_pos (dict): Results dict with all positives, labeled.
        """
        all_pos = {}

        # Cycle through each positive (TP or FP)
        for i in analyzer_results:
            analyzer_result = analyzer_results[i]

            # See if there are any ground truth matches
            all_pos, gt_match_found = cls._match_with_source(
                all_pos, gt_labels_dict, analyzer_result, tolerance
            )

            # If not, check back with OCR
            if not gt_match_found:
                all_pos, _ = cls._match_with_source(
                    all_pos, ocr_results, analyzer_result, tolerance
                )

        return all_pos

    @staticmethod
    def _calculate_precision(gt_labels_dict: dict, all_pos: dict) -> float:
        """Calculate precision.

        Args:
            gt_labels_dict (dict): Dictionary with ground truth labels.
            all_pos (dict): All Detected PHI (mapped back to have actual PHI text).

        Return:
            precision (float): Precision value.
        """
        # Get ground truth values
        gt = list(gt_labels_dict.keys())

        # Get all positives (all detected PHI, whether TP or FP)
        all_p = list(all_pos.keys())

        # Find True Positive (TP) and precision
        tp = [i for i in all_p if i in gt]
        precision = len(tp) / len(all_p)

        return precision

    @staticmethod
    def _calculate_recall(gt_labels_dict: dict, all_pos: dict) -> float:
        """Calculate recall.

        Args:
            gt_labels_dict (dict): Dictionary with ground truth labels.
            all_pos (dict): All Detected PHI (mapped back to have actual PHI text).

        Return:
            recall (float): Recall value.
        """
        # Get ground truth values
        gt = list(gt_labels_dict.keys())

        # Get all positives (all detected PHI, whether TP or FP)
        all_p = list(all_pos.keys())

        # Find True Positive (TP) and precision
        tp = [i for i in all_p if i in gt]
        recall = len(tp) / len(gt)

        return recall
