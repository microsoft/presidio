from typing import List, Tuple, Optional

from presidio_analyzer import Pattern, PatternRecognizer


class CreditCardRecognizer(PatternRecognizer):
    """
    Recognize common credit card numbers using regex + checksum.

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    :param replacement_pairs: List of tuples with potential replacement values
    for different strings to be used during pattern matching.
    This can allow a greater variety in input, for example by removing dashes or spaces.
    """

    PATTERNS = [
        Pattern(
            "All Credit Cards (weak)",
            r"\b((4\d{3})|(5[0-5]\d{2})|(6\d{3})|(1\d{3})|(3\d{3}))[- ]?(\d{3,4})[- ]?(\d{3,4})[- ]?(\d{3,5})\b",  # noqa: E501
            0.3,
        ),
        Pattern(
            "All Credit Cards (medium)",
            r"""\b(3[47][0-9]{13}) |
            ((6541|6556)[0-9]{12}) |
            (389[0-9]{11}) |
            (3(?:0[0-5]|[68][0-9])[0-9]{11}) |
            (65[4-9][0-9]{13}|64[4-9][0-9]{13}|6011[0-9]{12}|(622(?:12[6-9]|1[3-9][0-9]|[2-8][0-9][0-9]|9[01][0-9]|92[0-5])[0-9]{10})) | 
            (63[7-9][0-9]{13}) |
            ((?:2131|1800|35\d{3})\d{11}) |
            (9[0-9]{15}) |
            ((6304|6706|6709|6771)[0-9]{12,15}) |
            ((5018|5020|5038|6304|6759|6761|6763)[0-9]{8,15}) |
            ((5[1-5][0-9]{14}|2(22[1-9][0-9]{12}|2[3-9][0-9]{13}|[3-6][0-9]{14}|7[0-1][0-9]{13}|720[0-9]{12}))) |
            ((6334|6767)[0-9]{12}|(6334|6767)[0-9]{14}|(6334|6767)[0-9]{15}) |
            ((4903|4905|4911|4936|6333|6759)[0-9]{12}|(4903|4905|4911|4936|6333|6759)[0-9]{14}|(4903|4905|4911|4936|6333|6759)[0-9]{15}|564182[0-9]{10}|564182[0-9]{12}|564182[0-9]{13}|633110[0-9]{10}|633110[0-9]{12}|633110[0-9]{13}) |
            ((62[0-9]{14,17})) |
            (4[0-9]{12}(?:[0-9]{3})?) |
            ((?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}))
            \b""",
            0.5
        )
    ]

    CONTEXT = [
        "credit",
        "card",
        "visa",
        "mastercard",
        "cc ",
        "amex",
        "discover",
        "jcb",
        "diners",
        "maestro",
        "instapayment",

        "card verification",
        "card identification number",
        "cvn",
        "cid",
        "cvc2",
        "cvv2",
        "pin block",
        "security code",
        "security number",
        "security no",
        "issue number",
        "issue no",
        "cryptogramme",
        "numéro de sécurité",
        "numero de securite",
        "kreditkartenprüfnummer",
        "kreditkartenprufnummer",
        "prüfziffer",
        "prufziffer",
        "sicherheits Kode",
        "sicherheitscode",
        "sicherheitsnummer",
        "verfalldatum",
        "codice di verifica",
        "cod. sicurezza",
        "cod sicurezza",
        "n autorizzazione",
        "código",
        "codigo",
        "cod. seg",
        "cod seg",
        "código de segurança",
        "codigo de seguranca",
        "codigo de segurança",
        "código de seguranca",
        "cód. segurança",
        "cod. seguranca",
        "cod. segurança",
        "cód. seguranca",
        "cód segurança",
        "cod seguranca",
        "cod segurança",
        "cód seguranca",
        "número de verificação",
        "numero de verificacao",
        "ablauf",
        "gültig bis",
        "gültigkeitsdatum",
        "gultig bis",
        "gultigkeitsdatum",
        "scadenza",
        "data scad",
        "fecha de expiracion",
        "fecha de venc",
        "vencimiento",
        "válido hasta",
        "valido hasta",
        "vto",
        "data de expiração",
        "data de expiracao",
        "data em que expira",
        "validade",
        "valor",
        "vencimento",
        "transaction",
        "transaction number",
        "reference number",
        "セキュリティコード",
        "セキュリティ コード",
        "セキュリティナンバー",
        "セキュリティ ナンバー",
        "セキュリティ番号",

        "amex",
        "american express",
        "americanexpress",
        "americano espresso",
        "Visa",
        "mastercard",
        "master card",
        "mc",
        "mastercards",
        "master cards",
        "diner's Club",
        "diners club",
        "dinersclub",
        "discover",
        "discover card",
        "discovercard",
        "discover cards",
        "JCB",
        "BrandSmart",
        "japanese card bureau",
        "carte blanche",
        "carteblanche",
        "credit card",
        "cc#",
        "cc#:",
        "expiration date",
        "exp date",
        "expiry date",
        "date d'expiration",
        "date d'exp",
        "date expiration",
        "bank card",
        "bankcard",
        "card number",
        "card num",
        "cardnumber",
        "cardnumbers",
        "card numbers",
        "creditcard",
        "credit cards",
        "creditcards",
        "ccn",
        "card holder",
        "cardholder",
        "card holders",
        "cardholders",
        "check card",
        "checkcard",
        "check cards",
        "checkcards",
        "debit card",
        "debitcard",
        "debit cards",
        "debitcards",
        "atm card",
        "atmcard",
        "atm cards",
        "atmcards",
        "enroute",
        "en route",
        "card type",
        "Cardmember Acct",
        "cardmember account",
        "Cardno",
        "Corporate Card",
        "Corporate cards",
        "Type of card",
        "card account number",
        "card member account",
        "Cardmember Acct.",
        "card no.",
        "card no",
        "card number",
        "carte bancaire",
        "carte de crédit",
        "carte de credit",
        "numéro de carte",
        "numero de carte",
        "nº de la carte",
        "nº de carte",
        "kreditkarte",
        "karte",
        "karteninhaber",
        "karteninhabers",
        "kreditkarteninhaber",
        "kreditkarteninstitut",
        "kreditkartentyp",
        "eigentümername",
        "kartennr",
        "kartennummer",
        "kreditkartennummer",
        "kreditkarten-nummer",
        "carta di credito",
        "carta credito",
        "n. carta",
        "n carta",
        "nr. carta",
        "nr carta",
        "numero carta",
        "numero della carta",
        "numero di carta",
        "tarjeta credito",
        "tarjeta de credito",
        "tarjeta crédito",
        "tarjeta de crédito",
        "tarjeta de atm",
        "tarjeta atm",
        "tarjeta debito",
        "tarjeta de debito",
        "tarjeta débito",
        "tarjeta de débito",
        "nº de tarjeta",
        "no. de tarjeta",
        "no de tarjeta",
        "numero de tarjeta",
        "número de tarjeta",
        "tarjeta no",
        "tarjetahabiente",
        "cartão de crédito",
        "cartão de credito",
        "cartao de crédito",
        "cartao de credito",
        "cartão de débito",
        "cartao de débito",
        "cartão de debito",
        "cartao de debito",
        "débito automático",
        "debito automatico",
        "número do cartão",
        "numero do cartão",
        "número do cartao",
        "numero do cartao",
        "número de cartão",
        "numero de cartão",
        "número de cartao",
        "numero de cartao",
        "nº do cartão",
        "nº do cartao",
        "nº. do cartão",
        "no do cartão",
        "no do cartao",
        "no. do cartão",
        "no. do cartao",
        "rupay",
        "union pay",
        "unionpay",
        "diner's",
        "diners",
        "クレジットカード番号",
        "クレジットカードナンバー",
        "クレジットカード＃",
        "クレジットカード",
        "クレジット",
        "クレカ",
        "カード番号",
        "カードナンバー",
        "カード＃",
        "アメックス",
        "アメリカンエクスプレス",
        "アメリカン エクスプレス",
        "Visaカード",
        "Visa カード",
        "マスターカード",
        "マスター カード",
        "マスター",
        "ダイナースクラブ",
        "ダイナース クラブ",
        "ダイナース",
        "有効期限",
        "期限",
        "キャッシュカード",
        "キャッシュ カード",
        "カード名義人",
        "カードの名義人",
        "カードの名義",
        "デビット カード",
        "デビットカード",
        "中国银联",
        "银联",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "CREDIT_CARD",
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

    def validate_result(self, pattern_text: str) -> bool:  # noqa D102
        sanitized_value = self.__sanitize_value(pattern_text, self.replacement_pairs)
        checksum = self.__luhn_checksum(sanitized_value)

        return checksum

    @staticmethod
    def __luhn_checksum(sanitized_value: str) -> bool:
        def digits_of(n: str) -> List[int]:
            return [int(dig) for dig in str(n)]

        digits = digits_of(sanitized_value)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(str(d * 2)))
        return checksum % 10 == 0

    @staticmethod
    def __sanitize_value(text: str, replacement_pairs: List[Tuple[str, str]]) -> str:
        for search_string, replacement_string in replacement_pairs:
            text = text.replace(search_string, replacement_string)
        return text
