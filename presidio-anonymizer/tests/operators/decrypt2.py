from presidio_anonymizer.operators import Operator, Decrypt


class Decrypt2(Decrypt):
    """Decrypt text to from its encrypted form."""

    NAME = "decrypt2"
    PATTERN = r'@@@([\w\s\\]+)@@@'  # r'@@@(.*?)@@@' #

    def operate(self, text: str = None, params: Dict = None) -> str:
        """
        Decrypt the text.

        :param text: The text for decryption.
        :param params:
            **key* The key supplied by the user for the encryption.
        :return: The encrypted text
        """
        text = text.removeprefix('@@@')
        text = text.removesuffix('@@@')
        decrypted_text = super().operate(text, params)
        return decrypted_text
