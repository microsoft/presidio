from presidio_analyzer import RecognizerResult


class ImageRecognizerResult(RecognizerResult):
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

        super().__init__(entity_type, start, end, score)
        self.left = left
        self.top = top
        self.width = width
        self.height = height

    def __eq__(self, other):
        """
        Check two ImageRecognizerResult objects are equal by using all class fields.

        :param other: another ImageRecognizerResult object
        :return: bool
        """
        equal_type = self.entity_type == other.entity_type
        equal_pos = (self.start == other.start) and (self.end == other.end)
        equal_score = self.score == other.score
        equal_box1 = (self.left == other.left) and (self.top == other.top)
        equal_box2 = (self.width == other.width) and (self.height == other.height)
        equal_box = equal_box1 and equal_box2
        return equal_type and equal_pos and equal_score and equal_box
