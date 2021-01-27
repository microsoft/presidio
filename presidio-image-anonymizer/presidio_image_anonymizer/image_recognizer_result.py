class ImageRecognizerResult:
    """
    ImageRecognizerResult represents the results of analysing the image.

    :param entity_type: the type of the entity
    :param start: the start location of the detected entity in the text
    :param end: the end location of the detected entity in the text
    :param score: the score of the detection
    :param left: x coord of the top left corner of the bbox in pixels
    :param top: y coord of the top left corner of the bbox in pixels
    :param width: width of the bbox in pixels
    :param height: height of the bbox in pixels
    """

    def __init__(
        self,
        entity_type: str,
        start: int,
        end: int,
        score: float,
        left: int,
        top: int,
        width: int,
        height: int,
    ):

        self.entity_type = entity_type
        self.start = start
        self.end = end
        self.score = score
        self.left = left
        self.top = top
        self.width = width
        self.height = height
