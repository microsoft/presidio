from PIL import Image, ImageChops
from presidio_image_redactor.image_analyzer_engine import ImageAnalyzerEngine
import matplotlib
import io
from matplotlib import pyplot as plt


def fig2img(fig):
    """Convert a Matplotlib figure to a PIL Image and return it."""

    buf = io.BytesIO()
    fig.savefig(buf)
    buf.seek(0)
    img = Image.open(buf)
    return img


class ImagePiiVerifyEngine:
    """ImagePiiVerifyEngine class only supporting Pii verification currently."""

    def __init__(self):
        self.analyzer_engine = ImageAnalyzerEngine()

    def verify(self, image: Image) -> Image:
        """Annotate image with the detect PII entity.

        Please notice, this method duplicates the image, creates a new instance and
        manipulate it.
        :param image: PIL Image to be processed
        :return: the annotated image
        """

        image = ImageChops.duplicate(image)
        image_x, image_y = image.size
        analyzer_engine = ImageAnalyzerEngine()
        bboxes = analyzer_engine.analyze(image)
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
