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
from presidio_image_redactor import ImagePiiVerifyEngine, BboxProcessor
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

        # Initialize bbox processor
        self.bbox_processor = BboxProcessor()

    def verify_dicom_instance(
        self,
        instance: pydicom.dataset.FileDataset,
        padding_width: int = 25,
        display_image: bool = True,
        ocr_kwargs: Optional[dict] = None,
        **text_analyzer_kwargs,
    ) -> Tuple[Optional[PIL.Image.Image], dict, list]:
        """Verify PII on a single DICOM instance.

        :param instance: Loaded DICOM instance including pixel data and metadata.
        :param padding_width: Padding width to use when running OCR.
        :param display_image: If the verificationimage is displayed and returned.
        :param ocr_kwargs: Additional params for OCR methods.
        :param text_analyzer_kwargs: Additional values for the analyze method
        in ImageAnalyzerEngine.

        :return: Image with boxes identifying PHI, OCR results,
        and analyzer results.
        """
        instance_copy = deepcopy(instance)

        try:
            instance_copy.PixelData
        except AttributeError:
            raise AttributeError("Provided DICOM instance lacks pixel data.")

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
            ocr_kwargs=ocr_kwargs,
            ad_hoc_recognizers=[deny_list_recognizer],
            **text_analyzer_kwargs,
        )

        # Get image with verification boxes
        verify_image = (
            self.verify(
                image, ad_hoc_recognizers=[deny_list_recognizer], **text_analyzer_kwargs
            )
            if display_image
            else None
        )

        return verify_image, ocr_results, analyzer_results

    def eval_dicom_instance(
        self,
        instance: pydicom.dataset.FileDataset,
        ground_truth: dict,
        padding_width: int = 25,
        tolerance: int = 50,
        display_image: bool = False,
        ocr_kwargs: Optional[dict] = None,
        **text_analyzer_kwargs,
    ) -> Tuple[Optional[PIL.Image.Image], dict]:
        """Evaluate performance for a single DICOM instance.

        :param instance: Loaded DICOM instance including pixel data and metadata.
        :param ground_truth: Dictionary containing ground truth labels for the instance.
        :param padding_width: Padding width to use when running OCR.
        :param tolerance: Pixel distance tolerance for matching to ground truth.
        :param display_image: If the verificationimage is displayed and returned.
        :param ocr_kwargs: Additional params for OCR methods.
        :param text_analyzer_kwargs: Additional values for the analyze method
        in ImageAnalyzerEngine.

        :return: Evaluation comparing redactor engine results vs ground truth.
        """
        # Verify detected PHI
        verify_image, ocr_results, analyzer_results = self.verify_dicom_instance(
            instance,
            padding_width,
            display_image,
            ocr_kwargs=ocr_kwargs,
            **text_analyzer_kwargs,
        )
        formatted_ocr_results = self.bbox_processor.get_bboxes_from_ocr_results(
            ocr_results
        )
        detected_phi = self.bbox_processor.get_bboxes_from_analyzer_results(
            analyzer_results
        )

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
    def _remove_duplicate_entities(
        results: List[dict], dup_pix_tolerance: int = 5
    ) -> List[dict]:
        """Handle when a word is detected multiple times as different types of entities.

        :param results: List of detected PHI with bbox info.
        :param dup_pix_tolerance: Pixel difference tolerance for identifying duplicates.
        :return: Detected PHI with no duplicate entities.
        """
        dups = []
        sorted(results, key=lambda x: x['score'], reverse=True)
        results_no_dups = []
        dims = ["left", "top", "width", "height"]

        # Check for duplicates
        for i in range(len(results) - 1):
            i_dims = {dim: results[i][dim] for dim in dims}

            # Ignore if we've already detected this dup combination
            for other in range(i + 1, len(results)):
                if i not in results_no_dups:
                    other_dims = {dim: results[other][dim] for dim in dims}
                    matching_dims = {
                        dim: abs(i_dims[dim] - other_dims[dim]) <= dup_pix_tolerance
                        for dim in dims
                    }
                    matching = list(matching_dims.values())

                    if all(matching):
                        lower_scored_index = other if \
                            results[other]['score'] < results[i]['score'] else i
                        dups.append(lower_scored_index)

        # Remove duplicates
        for i in range(len(results)):
            if i not in dups:
                results_no_dups.append(results[i])

        return results_no_dups

    def _label_all_positives(
        self,
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
            all_pos, gt_match_found = self.bbox_processor.match_with_source(
                all_pos, gt_labels_dict, analyzer_result, tolerance
            )

            # If not, check back with OCR
            if not gt_match_found:
                all_pos, _ = self.bbox_processor.match_with_source(
                    all_pos, ocr_results, analyzer_result, tolerance
                )

        # Remove any duplicates
        all_pos = self._remove_duplicate_entities(all_pos)

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
            recall = 0

        return recall
