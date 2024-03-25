import re
from typing import List, Optional, Tuple
from presidio_analyzer import Pattern, PatternRecognizer
from presidio_analyzer.analyzer_utils import PresidioAnalyzerUtils as Utils


class CfiRecognizer(PatternRecognizer):
    """
    Recognize Classification of Financial Codes (CFI codes) using regex.

    Ref: 1. https://en.wikipedia.org/wiki/ISO_10962 .
    2. https://bit.ly/ISO10962-2021

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    PATTERNS = [
        Pattern(
            "CFI (Weak)",
            r"\b^[A-Z]{6}$\b",
            0.05,
        ),
        Pattern(
            "CFI (Medium)",
            r"\b^[ECDROFSHIJKLTM][A-Z]{5}$\b",
            0.10,
        ),
        Pattern(
            "CFI (Strong)",
            r"\b^(ES|EP|EC|EF|EL|ED|EY|EM|CI|CH|CB|CE|CS|CF|CP|CM|DB|DC|DW|DT|DS|DE|DG"
            r"|DA|DN|DD|DM|DY|RA|RS|RP|RW|RF|RD|RM|OC|OP|OM|FF|FC|SR|ST|SE|SC|SF|SM|HR"
            r"|HT|HE|HC|HF|HM|IF|IT|JE|JF|JC|JR|JT|KR|KT|KE|KC|KF|KY|KM|LL"
            r"|LR|LS|TC|TT|TR|TI|TB|TD|TM|MC|MM)[A-Z]{4}$\b",
            0.50,
        ),
    ]

    equity_regex_patterns = [
        r"\b^(ES)[VNRE]{1}[TU]{1}[FOP]{1}[BRNM]{1}$\b",
        r"\b^(E)[PF]{1}[VNRE]{1}[RETGACN]{1}[FCPQANUD]{1}[BRNM]{1}$\b",
        r"\b^(ED)[SPCFLM]{1}[RNBDX]{1}[FCPQANUD]{1}[BRNM]{1}$\b",
        r"\b^(EY)[ABCDEM]{1}[DYM]{1}[FVEM]{1}[BSDGTCINM]{1}$\b",
        r"\b^(E)[RV]{1}[VNRE]{1}[RETGACN]{1}[FCPQANUD]{1}[BRNM]{1}$\b",
        r"\b^(EU)[CO]{1}[IGM]{1}[RSMCD]{1}[BRNZAM]{1}$\b",
        r"\b^(EMXXX)[BRNM]{1}$\b",
    ]

    debt_regex_patterns = [
        r"\b(D)[BCWT]{1}[FZVCK]{1}[TGSUPNOQJC]{1}[FGCDABTLPQRE]{1}[BRNM]{1}\b",
        r"\b(DS)[ABCDM]{1}[FDYM]{1}[FVM]{1}[BSDTCIM]{1}\b",
        r"\b(DE)[ABCDEM]{1}[FDYM]{1}[RSCTM]{1}[BSDTCIM]{1}\b",
        r"\b(DG)[FZV]{1}[TGSUPNOQJC]{1}[FGCDABTLPQRE]{1}[BRNM]{1}\b",
        r"\b(D)[AN]{1}[FZV]{1}[TGSUPNOQJC]{1}[FGCDABTLPQRE]{1}[BRNM]{1}\b",
        r"\b(DD)[BCWTYGQNM]{1}[FZVC]{1}[TGSUPNOQJC]{1}[FGCDABTLPQRE]{1}\b",
        r"\b(DY)[FZVK]{1}[TGSUPNOQJC]{1}(X)[BRNM]{1}\b",
        r"\b(DM)[BPM]{1}(XX)[BRNM]{1}\b",
    ]

    collective_investment_regex_patterns = [
        r"\b(C)[PI]{1}[OCM]{1}[IGJ]{1}[RBEVLCDFKM]{1}[SQUY]{1}\b",
        r"\b(CMXXX)[SQUY]{1}\b",
        r"\b(CH)[DRSEANLM]{1}(XXX)\b",
        r"\b(CB)[OCM]{1}[IGJ]{1}(X)[SQUY]\b",
        r"\b(CE)[OCM]{1}[IGJ]{1}[RBEVLCDFKM]{1}[SU]{1}\b",
        r"\b(CS)[OCM]{1}[BGLM]{1}[RBM]{1}[SU]{1}\b",
        r"\b(CF)[OCM]{1}[IGJ]{1}[IHBEPM]{1}[SQUY]{1}\b",
    ]

    rights_regex_patterns = [
        r"\b(RAXXX)[BRNM]{1}\b",
        r"\b(R)[PS]{1}[SPCFBIM]{1}(XX)[BRNM]{1}\b",
        r"\b(RW)[BSDTCIM]{1}[TNC]{1}[CPB]{1}[AEBM]{1}\b",
        r"\b(RF)[BSDTCIM]{1}[TNM]{1}[CPM]{1}[AEBM]{1}\b",
        r"\b(RD)[ASPWM]{1}(XX)[BRNM]{1}\b",
        r"\b(RMXXXX)\b",
    ]

    listed_options_regex_patterns = [
        r"\b(O)[CP]{1}[AEB]{1}[BSDTCIOFWNM]{1}[PCNE]{1}[SN]{1}\b",
        r"\b(OMXXXX)\b",
    ]

    futures_regex_patterns = [
        r"\b(FF)[BSDCIOFWNVM]{1}[PCN]{1}[SN]{1}(X)\b",
        r"\b(FC)[EAISNPHM]{1}[PCN]{1}[SN]{1}(X)\b",
    ]

    swaps_regex_patterns = [
        r"\b(SR)[ACDGHZM]{1}[CDIY]{1}[SC]{1}[CP]{1}\b",
        r"\b(ST)[JKANGPSTIQM]{1}[PDVLTCM]{1}(X)[CPE]{1}\b",
        r"\b(SE)[SIBM]{1}[PDVLTCM]{1}(X)[CPE]{1}\b",
        r"\b(SC)[UVIBM]{1}[CTM]{1}[CSL]{1}[CPA]{1}\b",
        r"\b(SF)[ACM]{1}(XX)[PN]{1}\b",
        r"\b(SM)[PM]{1}(XX)[CP]{1}\b",
    ]

    non_listed_regex_patterns = [
        r"\b(HR)[ACDGHORFM]{1}[ABCDEFGHI]{1}[VADBGLPM]{1}[CPE]{1}\b",
        r"\b(HT)[JKANGPSTIQORFWM][ABCDEFGHI]{1}[VADBGLPM]{1}[CPE]{1}\b",
        r"\b(HE)[SIBORFM]{1}[ABCDEFGHI]{1}[VADBGLPM]{1}[CPE]{1}\b",
        r"\b(HC)[UVIWM]{1}[ABCDEFGHI]{1}[VADBGLPM]{1}[CPE]{1}\b",
        r"\b(HF)[RFTVM]{1}[ABCDEFGHI]{1}[VADBGLPM]{1}[CPEN{1}\b",
        r"\b(HM)[PM]{1}[ABCDEFGHI]{1}[VADBGLPM]{1}[CPENA]{1}\b",
    ]

    spot_regex_patterns = [
        r"\b(IFXXXP)\b",
        r"\b(IT)[AJKNPSTM]{1}(XXX)\b",
    ]

    forwards_regex_patterns = [
        r"\b(JE)[SIBOF]{1}(X)[CSF]{1}[CP]{1}\b",
        r"\b(JF)[TROF]{1}(X)[CSF]{1}[PCN]{1}\b",
        r"\b(JC)[AIBCDGO]{1}(X)[SF]{1}[PCN]{1}\b",
        r"\b(JR)[IOM]{1}(X)[SF]{1}[PCN]{1}\b",
        r"\b(JT)[ABGIJKNPSTM]{1}(X)[CF]{1}[PCN]{1}\b",
    ]

    strategies_regex_patterns = [
        r"\b(K)[RTECFYM]{1}(XXXX)\b",
    ]

    financing_regex_patterns = [
        r"\b(LL)[ABJKNPSTM]{1}(XX)[PCN]{1}\b",
        r"\b(LR)[GSC]{1}[FNOT]{1}(X)[DHT]{1}\b",
        r"\b(LS)[CGPTELDWKM]{1}[NOT]{1}(X)[DHFT]{1}\b",
    ]
    reference_instruments_regex_patterns = [
        r"\b(TC)[NCLM]{1}(XXX)\b",
        r"\b(TT)[EAISNPHM]{1}(XXX)\b",
        r"\b(TR)[NVFRM]{1}[DWNQSAM]{1}(XX)\b",
        r"\b(TI)[EDFRTCM]{1}[PCEFM]{1}[PNGM]{1}(X)\b",
        r"\b(TB)[EDFITCM]{1}(XXX)\b",
        r"\b(TD)[SPCFLKM](XXX)\b",
        r"\b(TMXXXX)\b",
    ]
    miscellaneous_regex_patterns = [
        r"\b(MC)[SBHAWUM]{1}[TU]{1}(X)[BRNM]\b",
        r"\b(MM)[RIETNPSM]{1}(XXX)\b",
    ]

    regex_options = {
        "E": equity_regex_patterns,
        "C": collective_investment_regex_patterns,
        "D": debt_regex_patterns,
        "R": rights_regex_patterns,
        "O": listed_options_regex_patterns,
        "F": futures_regex_patterns,
        "S": swaps_regex_patterns,
        "H": non_listed_regex_patterns,
        "I": spot_regex_patterns,
        "J": forwards_regex_patterns,
        "K": strategies_regex_patterns,
        "L": financing_regex_patterns,
        "T": reference_instruments_regex_patterns,
        "M": miscellaneous_regex_patterns,
    }

    CONTEXT = ["CFI", "CFI_CODE"]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        replacement_pairs: Optional[List[Tuple[str, str]]] = None,
        supported_language: str = "en",
        supported_entity: str = "CFI_CODE",
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
        return self.__check_cfi(sanitized_value)

    def __check_cfi(self, sanitized_value: str) -> bool:
        is_valid_cfi = None
        if sanitized_value and len(sanitized_value) == 6 and sanitized_value.isalpha():
            applicable_regex_patterns = self.regex_options.get(sanitized_value[0], None)
            if applicable_regex_patterns and len(applicable_regex_patterns) > 0:
                pattern = re.compile(
                    "|".join(applicable_regex_patterns),
                    flags=re.DOTALL | re.IGNORECASE | re.MULTILINE,
                )
                groups = re.match(pattern, sanitized_value)
                if groups:
                    is_valid_cfi = True
        return is_valid_cfi
