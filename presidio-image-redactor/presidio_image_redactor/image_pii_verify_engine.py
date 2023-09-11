from PIL import Image, ImageChops
from presidio_image_redactor.image_redactor_engine import ImageRedactorEngine
from presidio_analyzer import PatternRecognizer
import matplotlib
import io
from matplotlib import pyplot as plt
from typing import Optional, List


def fig2img(fig):
    """Convert a Matplotlib figure to a PIL Image and return it."""

    buf = io.BytesIO()
    fig.savefig(buf)
    buf.seek(0)
    img = Image.open(buf)
    return img


class ImagePiiVerifyEngine(ImageRedactorEngine):
    """ImagePiiVerifyEngine class only supporting Pii verification currently."""

    def verify(
        self,
        image: Image,
        ocr_kwargs: Optional[dict] = None,
        ad_hoc_recognizers: Optional[List[PatternRecognizer]] = None,
        **text_analyzer_kwargs
    ) -> Image:
        """Annotate image with the detect PII entity.

        Please notice, this method duplicates the image, creates a
        new instance and manipulate it.

        :param image: PIL Image to be processed.
        :param ocr_kwargs: Additional params for OCR methods.
        :param ad_hoc_recognizers: List of PatternRecognizer objects to use
        for ad-hoc recognizer.
        :param text_analyzer_kwargs: Additional values for the analyze method
        in ImageAnalyzerEngine.

        :return: the annotated image
        """

        image = ImageChops.duplicate(image)
        image_x, image_y = image.size

        # Detect PII
        self._check_ad_hoc_recognizer_list(ad_hoc_recognizers)
        if ad_hoc_recognizers is None:
            bboxes = self.image_analyzer_engine.analyze(
                image,
                ocr_kwargs=ocr_kwargs,
                **text_analyzer_kwargs,
            )
        else:
            bboxes = self.image_analyzer_engine.analyze(
                image,
                ocr_kwargs=ocr_kwargs,
                ad_hoc_recognizers=ad_hoc_recognizers,
                **text_analyzer_kwargs,
            )

        fig, ax = plt.subplots()
        image_r = 70
        fig.set_size_inches(image_x / image_r, image_y / image_r)
        if len(bboxes) == 0:
            return image
        else:
            for box in bboxes:
                entity_type = box.entity_type
                x0 = box.left
                y0 = box.top
                x1 = x0 + box.width
                y1 = y0 + box.height
                rect = matplotlib.patches.Rectangle(
                    (x0, y0), x1 - x0, y1 - y0, edgecolor="b", facecolor="none"
                )
                ax.add_patch(rect)
                ax.annotate(
                    entity_type,
                    xy=(x0 - 3, y0 - 3),
                    xycoords="data",
                    bbox=dict(boxstyle="round4,pad=.5", fc="0.9"),
                )
            ax.imshow(image)
            im_from_fig = fig2img(fig)
            im_resized = im_from_fig.resize((image_x, image_y))
            return im_resized
