from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer


class UrlRecognizer(PatternRecognizer):
    """
    Recognize urls using regex.

    This application uses Open Source components:
    Project: CommonRegex https://github.com/madisonmay/CommonRegex
    Copyright (c) 2014 Madison May
    License (MIT)  https://github.com/madisonmay/CommonRegex/blob/master/LICENSE

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    PATTERNS = [
        Pattern("Standard Url",
                r"(?i)(?:https?://)((www\d{0,3}[.])?[a-z0-9.\-]+[.](?:(?:com)|("
                r"?:edu)|(?:gov)|(?:int)|(?:mil)|( "
                r"?:net)|(?:onl)|(?:org)|(?:pro)|(?:red)|(?:tel)|(?:uno)|(?:xxx)|("
                r"?:ac)|(?:ad)|(?:ae)|(?:af)|(?:ag)|( "
                r"?:ai)|(?:al)|(?:am)|(?:an)|(?:ao)|(?:aq)|(?:ar)|(?:as)|(?:at)|("
                r"?:au)|(?:aw)|(?:ax)|(?:az)|(?:ba)|( "
                r"?:bb)|(?:bd)|(?:be)|(?:bf)|(?:bg)|(?:bh)|(?:bi)|(?:bj)|(?:bm)|("
                r"?:bn)|(?:bo)|(?:br)|(?:bs)|(?:bt)|( "
                r"?:bv)|(?:bw)|(?:by)|(?:bz)|(?:ca)|(?:cc)|(?:cd)|(?:cf)|(?:cg)|("
                r"?:ch)|(?:ci)|(?:ck)|(?:cl)|(?:cm)|( "
                r"?:cn)|(?:co)|(?:cr)|(?:cu)|(?:cv)|(?:cw)|(?:cx)|(?:cy)|(?:cz)|("
                r"?:de)|(?:dj)|(?:dk)|(?:dm)|(?:do)|( "
                r"?:dz)|(?:ec)|(?:ee)|(?:eg)|(?:er)|(?:es)|(?:et)|(?:eu)|(?:fi)|("
                r"?:fj)|(?:fk)|(?:fm)|(?:fo)|(?:fr)|( "
                r"?:ga)|(?:gb)|(?:gd)|(?:ge)|(?:gf)|(?:gg)|(?:gh)|(?:gi)|(?:gl)|("
                r"?:gm)|(?:gn)|(?:gp)|(?:gq)|(?:gr)|( "
                r"?:gs)|(?:gt)|(?:gu)|(?:gw)|(?:gy)|(?:hk)|(?:hm)|(?:hn)|(?:hr)|("
                r"?:ht)|(?:hu)|(?:id)|(?:ie)|(?:il)|( "
                r"?:im)|(?:in)|(?:io)|(?:iq)|(?:ir)|(?:is)|(?:it)|(?:je)|(?:jm)|("
                r"?:jo)|(?:jp)|(?:ke)|(?:kg)|(?:kh)|( "
                r"?:ki)|(?:km)|(?:kn)|(?:kp)|(?:kr)|(?:kw)|(?:ky)|(?:kz)|(?:la)|("
                r"?:lb)|(?:lc)|(?:li)|(?:lk)|(?:lr)|( "
                r"?:ls)|(?:lt)|(?:lu)|(?:lv)|(?:ly)|(?:ma)|(?:mc)|(?:md)|(?:me)|("
                r"?:mg)|(?:mh)|(?:mk)|(?:ml)|(?:mm)|( "
                r"?:mn)|(?:mo)|(?:mp)|(?:mq)|(?:mr)|(?:ms)|(?:mt)|(?:mu)|(?:mv)|("
                r"?:mw)|(?:mx)|(?:my)|(?:mz)|(?:na)|( "
                r"?:nc)|(?:ne)|(?:nf)|(?:ng)|(?:ni)|(?:nl)|(?:no)|(?:np)|(?:nr)|("
                r"?:nu)|(?:nz)|(?:om)|(?:pa)|(?:pe)|( "
                r"?:pf)|(?:pg)|(?:ph)|(?:pk)|(?:pl)|(?:pm)|(?:pn)|(?:pr)|(?:ps)|("
                r"?:pt)|(?:pw)|(?:py)|(?:qa)|(?:re)|( "
                r"?:ro)|(?:rs)|(?:ru)|(?:rw)|(?:sa)|(?:sb)|(?:sc)|(?:sd)|(?:se)|("
                r"?:sg)|(?:sh)|(?:si)|(?:sj)|(?:sk)|( "
                r"?:sl)|(?:sm)|(?:sn)|(?:so)|(?:sr)|(?:st)|(?:su)|(?:sv)|(?:sx)|("
                r"?:sy)|(?:sz)|(?:tc)|(?:td)|(?:tf)|( "
                r"?:tg)|(?:th)|(?:tj)|(?:tk)|(?:tl)|(?:tm)|(?:tn)|(?:to)|(?:tp)|("
                r"?:tr)|(?:tt)|(?:tv)|(?:tw)|(?:tz)|( "
                r"?:ua)|(?:ug)|(?:uk)|(?:us)|(?:uy)|(?:uz)|(?:va)|(?:vc)|(?:ve)|("
                r"?:vg)|(?:vi)|(?:vn)|(?:vu)|(?:wf)|(?:ws)|(?:ye)|(?:yt)|(?:za)|("
                r"?:zm)|(?:zw))(?:/[^\s()<>]+|/)?)",
                0.6),
        Pattern("Non schema URL",
                r"(?i)((www\d{0,3}[.])?[a-z0-9.\-]+[.](?:(?:com)|("
                r"?:edu)|(?:gov)|(?:int)|(?:mil)|( "
                r"?:net)|(?:onl)|(?:org)|(?:pro)|(?:red)|(?:tel)|(?:uno)|(?:xxx)|("
                r"?:ac)|(?:ad)|(?:ae)|(?:af)|(?:ag)|( "
                r"?:ai)|(?:al)|(?:am)|(?:an)|(?:ao)|(?:aq)|(?:ar)|(?:as)|(?:at)|("
                r"?:au)|(?:aw)|(?:ax)|(?:az)|(?:ba)|( "
                r"?:bb)|(?:bd)|(?:be)|(?:bf)|(?:bg)|(?:bh)|(?:bi)|(?:bj)|(?:bm)|("
                r"?:bn)|(?:bo)|(?:br)|(?:bs)|(?:bt)|( "
                r"?:bv)|(?:bw)|(?:by)|(?:bz)|(?:ca)|(?:cc)|(?:cd)|(?:cf)|(?:cg)|("
                r"?:ch)|(?:ci)|(?:ck)|(?:cl)|(?:cm)|( "
                r"?:cn)|(?:co)|(?:cr)|(?:cu)|(?:cv)|(?:cw)|(?:cx)|(?:cy)|(?:cz)|("
                r"?:de)|(?:dj)|(?:dk)|(?:dm)|(?:do)|( "
                r"?:dz)|(?:ec)|(?:ee)|(?:eg)|(?:er)|(?:es)|(?:et)|(?:eu)|(?:fi)|("
                r"?:fj)|(?:fk)|(?:fm)|(?:fo)|(?:fr)|( "
                r"?:ga)|(?:gb)|(?:gd)|(?:ge)|(?:gf)|(?:gg)|(?:gh)|(?:gi)|(?:gl)|("
                r"?:gm)|(?:gn)|(?:gp)|(?:gq)|(?:gr)|( "
                r"?:gs)|(?:gt)|(?:gu)|(?:gw)|(?:gy)|(?:hk)|(?:hm)|(?:hn)|(?:hr)|("
                r"?:ht)|(?:hu)|(?:id)|(?:ie)|(?:il)|( "
                r"?:im)|(?:in)|(?:io)|(?:iq)|(?:ir)|(?:is)|(?:it)|(?:je)|(?:jm)|("
                r"?:jo)|(?:jp)|(?:ke)|(?:kg)|(?:kh)|( "
                r"?:ki)|(?:km)|(?:kn)|(?:kp)|(?:kr)|(?:kw)|(?:ky)|(?:kz)|(?:la)|("
                r"?:lb)|(?:lc)|(?:li)|(?:lk)|(?:lr)|( "
                r"?:ls)|(?:lt)|(?:lu)|(?:lv)|(?:ly)|(?:ma)|(?:mc)|(?:md)|(?:me)|("
                r"?:mg)|(?:mh)|(?:mk)|(?:ml)|(?:mm)|( "
                r"?:mn)|(?:mo)|(?:mp)|(?:mq)|(?:mr)|(?:ms)|(?:mt)|(?:mu)|(?:mv)|("
                r"?:mw)|(?:mx)|(?:my)|(?:mz)|(?:na)|( "
                r"?:nc)|(?:ne)|(?:nf)|(?:ng)|(?:ni)|(?:nl)|(?:no)|(?:np)|(?:nr)|("
                r"?:nu)|(?:nz)|(?:om)|(?:pa)|(?:pe)|( "
                r"?:pf)|(?:pg)|(?:ph)|(?:pk)|(?:pl)|(?:pm)|(?:pn)|(?:pr)|(?:ps)|("
                r"?:pt)|(?:pw)|(?:py)|(?:qa)|(?:re)|( "
                r"?:ro)|(?:rs)|(?:ru)|(?:rw)|(?:sa)|(?:sb)|(?:sc)|(?:sd)|(?:se)|("
                r"?:sg)|(?:sh)|(?:si)|(?:sj)|(?:sk)|( "
                r"?:sl)|(?:sm)|(?:sn)|(?:so)|(?:sr)|(?:st)|(?:su)|(?:sv)|(?:sx)|("
                r"?:sy)|(?:sz)|(?:tc)|(?:td)|(?:tf)|( "
                r"?:tg)|(?:th)|(?:tj)|(?:tk)|(?:tl)|(?:tm)|(?:tn)|(?:to)|(?:tp)|("
                r"?:tr)|(?:tt)|(?:tv)|(?:tw)|(?:tz)|( "
                r"?:ua)|(?:ug)|(?:uk)|(?:us)|(?:uy)|(?:uz)|(?:va)|(?:vc)|(?:ve)|("
                r"?:vg)|(?:vi)|(?:vn)|(?:vu)|(?:wf)|(?:ws)|(?:ye)|(?:yt)|(?:za)|("
                r"?:zm)|(?:zw))(?:/[^\s()<>]+|/)?)",
                0.5)
    ]

    CONTEXT = ["url", "website", "link"]

    def __init__(
            self,
            patterns: Optional[List[Pattern]] = None,
            context: Optional[List[str]] = None,
            supported_language: str = "en",
            supported_entity: str = "URL",
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )
