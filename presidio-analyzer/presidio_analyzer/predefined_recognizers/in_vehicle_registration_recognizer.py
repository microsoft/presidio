from presidio_analyzer import Pattern, PatternRecognizer
from typing import Optional, List, Tuple
from presidio_analyzer.analyzer_utils import PresidioAnalyzerUtils as Utils


class InVehicleRegistrationRecognizer(PatternRecognizer):
    """
    Recognizes Indian Vehicle Registration Number issued by RTO.

    Reference(s):
    https://en.wikipedia.org/wiki/Vehicle_registration_plates_of_India
    https://en.wikipedia.org/wiki/Regional_Transport_Office
    https://en.wikipedia.org/wiki/List_of_Regional_Transport_Office_districts_in_India

    The registration scheme changed over time with multiple formats
    in play over the years
    India has multiple active patterns for registration plates issued to different
    vehicle categories

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    :param replacement_pairs: List of tuples with potential replacement values
        for different strings to be used during pattern matching.
    This can allow a greater variety in input e.g. by removing dashes or spaces
    """

    PATTERNS = [
        Pattern(
            "India Vehicle Registration (Very Weak)",
            r"\b[A-Z]{1}(?!0000)[0-9]{4}\b",
            0.01,
        ),
        Pattern(
            "India Vehicle Registration (Very Weak)",
            r"\b[A-Z]{2}(?!0000)\d{4}\b",
            0.01,
        ),
        Pattern(
            "India Vehicle Registration (Very Weak)",
            r"\b(I)(?!00000)\d{5}\b",
            0.01,
        ),
        Pattern(
            "India Vehicle Registration (Weak)",
            r"\b[A-Z]{3}(?!0000)\d{4}\b",
            0.2,
        ),
        Pattern(
            "India Vehicle Registration (Medium)",
            r"\b\d{1,3}(CD|CC|UN)[1-9]{1}[0-9]{1,3}\b",
            0.40,
        ),
        Pattern(
            "India Vehicle Registration",
            r"\b[A-Z]{2}\d{1,2}[A-Z]{1,2}(?!0000)\d{4}\b",
            0.50,
        ),
        Pattern(
            "India Vehicle Registration",
            r"\b[2-9]{1}[1-9]{1}(BH)(?!0000)\d{4}[A-HJ-NP-Z]{2}\b",
            0.85,
        ),
        Pattern(
            "India Vehicle Registration",
            r"\b(?!00)\d{2}(A|B|C|D|E|F|H|K|P|R|X)\d{6}[A-Z]{1}\b",
            0.85,
        ),
    ]

    CONTEXT = ["RTO", "vehicle", "plate", "registration"]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "IN_VEHICLE_REGISTRATION",
        replacement_pairs: Optional[List[Tuple[str, str]]] = None,
    ):
        self.replacement_pairs = (
            replacement_pairs
            if replacement_pairs
            else [("-", ""), (" ", ""), (":", "")]
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
        # print('Sanitized value:' + sanitized_value)
        return self.__check_vehicle_registration(sanitized_value)

    def __check_vehicle_registration(self, sanitized_value: str) -> bool:
        # print('check function called')
        is_valid_registration = None
        # logic here
        state_rto_districtcode_map = {
            "AN": Utils.in_vehicle_dist_an,
            "AP": Utils.in_vehicle_dist_ap,
            "AR": Utils.in_vehicle_dist_ar,
            "AS": Utils.in_vehicle_dist_as,
            "BR": Utils.in_vehicle_dist_br,
            "CG": Utils.in_vehicle_dist_cg,
            "CH": Utils.in_vehicle_dist_ch,
            "DD": Utils.in_vehicle_dist_dd,
            "DN": Utils.in_vehicle_dist_dn,
            "DL": Utils.in_vehicle_dist_dl,
            "GA": Utils.in_vehicle_dist_ga,
            "GJ": Utils.in_vehicle_dist_gj,
            "HP": Utils.in_vehicle_dist_hp,
            "HR": Utils.in_vehicle_dist_hr,
            "JH": Utils.in_vehicle_dist_jh,
            "JK": Utils.in_vehicle_dist_jk,
            "KA": Utils.in_vehicle_dist_ka,
            "KL": Utils.in_vehicle_dist_kl,
            "LA": Utils.in_vehicle_dist_la,
            "LD": Utils.in_vehicle_dist_ld,
            "MH": Utils.in_vehicle_dist_mh,
            "ML": Utils.in_vehicle_dist_ml,
            "MN": Utils.in_vehicle_dist_mn,
            "MP": Utils.in_vehicle_dist_mp,
            "MZ": Utils.in_vehicle_dist_mz,
            "NL": Utils.in_vehicle_dist_nl,
            "OD": Utils.in_vehicle_dist_od,
            "OR": Utils.in_vehicle_dist_or,
            "PB": Utils.in_vehicle_dist_pb,
            "PY": Utils.in_vehicle_dist_py,
            "RJ": Utils.in_vehicle_dist_rj,
            "SK": Utils.in_vehicle_dist_sk,
            "TN": Utils.in_vehicle_dist_tn,
            "TR": Utils.in_vehicle_dist_tr,
            "TS": Utils.in_vehicle_dist_ts,
            "UK": Utils.in_vehicle_dist_uk,
            "UP": Utils.in_vehicle_dist_up,
            "WB": Utils.in_vehicle_dist_wb,
        }
        two_factor_registration_prefix = []
        two_factor_registration_prefix.extend(Utils.in_union_territories)
        two_factor_registration_prefix.extend(Utils.in_states)
        two_factor_registration_prefix.extend(Utils.in_old_states)
        two_factor_registration_prefix.extend(Utils.in_old_union_territories)
        two_factor_registration_prefix.extend(Utils.in_non_standard_state_or_ut)
        first_two_char = sanitized_value[:2].upper()
        dist_code: str = ""

        if first_two_char in two_factor_registration_prefix:
            if sanitized_value[2].isdigit():
                if sanitized_value[3].isdigit():
                    dist_code = sanitized_value[2:4]
                else:
                    dist_code = sanitized_value[2:3]

                registration_digits = sanitized_value[-4:]
                if registration_digits.isnumeric():
                    if 0 < int(registration_digits) <= 9999:
                        if dist_code and dist_code in state_rto_districtcode_map.get(
                            first_two_char, ""
                        ):
                            is_valid_registration = True

            for diplomatic_vehicle_code in Utils.in_vehicle_diplomatic_codes:
                if diplomatic_vehicle_code in sanitized_value:
                    vehicle_prefix = sanitized_value.partition(diplomatic_vehicle_code)[
                        0
                    ]
                    if vehicle_prefix.isnumeric() and (
                        1 <= int(vehicle_prefix) <= 80
                        or int(vehicle_prefix) in Utils.in_vehicle_foreign_mission_codes
                    ):
                        is_valid_registration = True

        return is_valid_registration
