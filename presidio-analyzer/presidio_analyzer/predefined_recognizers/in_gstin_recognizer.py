from typing import Optional, List, Tuple
from presidio_analyzer import Pattern, PatternRecognizer
from presidio_analyzer.analyzer_utils import PresidioAnalyzerUtils as Utils
import pycountry


class InGstinRecognizer(PatternRecognizer):
    """
    Recognizes Indian Goods and Services Tax Identification Number ("GSTIN").

    The GSTIN  is a fifteen character alpha-numeric code
    with the last digit being a check digit calculated using a
    modified modulus 36 LUHN calculation.
    This recognizer identifies GSTIN using regex, context words and calculated value.
    Reference: https://en.wikipedia.org/wiki/Goods_and_Services_Tax_(India),
               http://idtc-icai.s3.amazonaws.com/download/knowledgeShare18-19/Structure-of-GSTIN.pdf

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    :param replacement_pairs: List of tuples with potential replacement values
    for different strings to be used during pattern matching.
    This can allow a greater variety in input, for example by removing dashes or spaces.
    """

    gstin_country_codes_iso3a = ""
    countries = pycountry.countries
    for country in countries:
        gstin_country_codes_iso3a += country.alpha_3 + "|"
    pattern1 = (
        "[0-9]{4}"
        + "("
        + gstin_country_codes_iso3a.rstrip("|")
        + ")"
        + "(?!00000)[0-9]{5}[A-Z]{2}[A-Z0-9]{1}"
    )

    pattern2 = (
        "[0-9]{2}[A-Z]{3}[ABCFGHJLPT]{1}[A-Z]{1}(?!0000)[0-9]{4}"
        + "[A-Z]{1}[1-9A-Z]{1}(Z)[0-9A-Z]{1}"
    )

    PATTERNS = [
        Pattern(
            "GSTIN (High)",
            pattern2,
            0.85,
        ),  # Regular registration pattern
        Pattern(
            "GSTIN (Low)",
            r"\b([0-9]{2}[A-Z]{5}(?!0000)[0-9]{4}[A-Z]{1}[0-9A-Z]{2})\b",
            0.2,
        ),
        Pattern("GSTIN (Medium)", pattern1, 0.6),  # NRTP pattern
        Pattern(
            "GSTIN (Very Low)",
            r"\b((?=.*?[A-Z])(?=.*?[0-9]{4})[\w@#$%^?~-]{10})\b",
            0.05,
        ),
    ]

    CONTEXT = [
        "GSTIN",
        "GST",
    ]

    _in_state_tin_codes = {
        "01": "Jammu and Kashmir",
        "02": "Himachal Pradesh",
        "03": "Punjab",
        "04": "Chandigarh",
        "05": "Uttarakhand",
        "06": "Haryana",
        "07": "Delhi",
        "08": "Rajasthan",
        "09": "Uttar Pradesh",
        "10": "Bihar",
        "11": "Sikkim",
        "12": "Arunachal Pradesh",
        "13": "Nagaland",
        "14": "Manipur",
        "15": "Mizoram",
        "16": "Tripura",
        "17": "Meghalaya",
        "18": "Assam",
        "19": "West Bengal",
        "20": "Jharkhand",
        "21": "Orissa",
        "22": "Chattisgarh",
        "23": "Madhya Pradesh",
        "24": "Gujarat",
        "25": "Daman and Diu",
        "26": "Dadar and Nagar Haveli",
        "27": "Maharashtra",
        "28": "Andhra Pradesh",
        "29": "Karnataka",
        "30": "Goa",
        "31": "Lakshadweep",
        "32": "Kerala",
        "33": "Tamil Nadu",
        "34": "Puducherry",
        "35": "Anadaman and Nicobar Islands",
        "36": "Telangana",
        "37": "Andhra Pradesh (New)",
    }

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "IN_GSTIN",
        replacement_pairs: Optional[List[Tuple[str, str]]] = None,
    ):
        self.replacement_pairs = (
            replacement_pairs if replacement_pairs else [("-", ""), (" ", "")]
        )
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )

    def validate_result(self, pattern_text: str) -> bool:
        """Determine absolute value based on calculation."""
        sanitized_value = Utils.sanitize_value(pattern_text, self.replacement_pairs)
        return self.__check_gstin(sanitized_value)

    def __check_gstin(self, sanitized_value: str) -> bool:
        is_valid_gstin = None  # deliberately set to None and not typecast either
        if sanitized_value and len(sanitized_value) == 15 and sanitized_value.isalnum():
            if sanitized_value[0:2] not in self._in_state_tin_codes:
                pass  # NRTP pattern detection only. As rules are not published yet
            else:
                if sanitized_value[13] != "Z" or sanitized_value[12] == "0":
                    is_valid_gstin = False
                elif Utils.get_luhn_mod_n(sanitized_value):
                    is_valid_gstin = True
                else:
                    is_valid_gstin = False
        else:
            is_valid_gstin = False

        return is_valid_gstin
