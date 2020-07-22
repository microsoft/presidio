"""
The IBAN patterns are based on the IBAN specification here:
https://en.wikipedia.org/wiki/International_Bank_Account_Number
In addition, an IBAN example per country can be found here:
git shttps://www.xe.com/ibancalculator/countrylist
An IBAN checker is available here: https://www.iban.com/iban-checker
"""

# IBAN parts format
CC = u"[A-Z]{2}"  # country code
CK = u"[0-9]{2}[ ]?"  # checksum
BOS = u"^"
EOS = u"$"  # end of string

A = u"[A-Z][ ]?"
A2 = u"([A-Z][ ]?){2}"
A3 = u"([A-Z][ ]?){3}"
A4 = u"([A-Z][ ]?){4}"

C = u"[a-zA-Z0-9][ ]?"
C2 = u"([a-zA-Z0-9][ ]?){2}"
C3 = u"([a-zA-Z0-9][ ]?){3}"
C4 = u"([a-zA-Z0-9][ ]?){4}"

N = u"[0-9][ ]?"
N2 = u"([0-9][ ]?){2}"
N3 = u"([0-9][ ]?){3}"
N4 = u"([0-9][ ]?){4}"

regex_per_country = {
    # Albania (8n, 16c) ALkk bbbs sssx cccc cccc cccc cccc
    "AL": u"(AL)" + CK + N4 + N4 + C4 + C4 + C4 + C4,
    # Andorra (8n, 12c) ADkk bbbb ssss cccc cccc cccc
    "AD": u"(AD)" + CK + N4 + N4 + C4 + C4 + C4,
    # Austria (16n) ATkk bbbb bccc cccc cccc
    "AT": u"(AT)" + CK + N4 + N4 + N4 + N4,
    # Azerbaijan    (4c,20n) AZkk bbbb cccc cccc cccc cccc cccc
    "AZ": u"(AZ)" + CK + C4 + N4 + N4 + N4 + N4 + N4,
    # Bahrain   (4a,14c)    BHkk bbbb cccc cccc cccc cc
    "BH": u"(BH)" + CK + A4 + C4 + C4 + C4 + C2,
    # Belarus (4c, 4n, 16c)   BYkk bbbb aaaa cccc cccc cccc cccc
    "BY": u"(BY)" + CK + C4 + N4 + C4 + C4 + C4 + C4,
    # Belgium (12n)   BEkk bbbc cccc ccxx
    "BE": u"(BE)" + CK + N4 + N4 + N4,
    # Bosnia and Herzegovina    (16n)   BAkk bbbs sscc cccc ccxx
    "BA": u"(BA)" + CK + N4 + N4 + N4 + N4,
    # Brazil (23n,1a,1c) BRkk bbbb bbbb ssss sccc cccc ccct n
    "BR": u"(BR)" + CK + N4 + N4 + N4 + N4 + N4 + N3 + A + C,
    # Bulgaria  (4a,6n,8c)  BGkk bbbb ssss ttcc cccc cc
    "BG": u"(BG)" + CK + A4 + N4 + N + N + C2 + C4 + C2,
    # Costa Rica    (18n)   CRkk 0bbb cccc cccc cccc cc (0 = always zero)
    "CR": u"(CR)" + CK + u"[0]" + N3 + N4 + N4 + N4 + N2,
    # Croatia   (17n)   HRkk bbbb bbbc cccc cccc c
    "HR": u"(HR)" + CK + N4 + N4 + N4 + N4 + N,
    # Cyprus    (8n,16c)    CYkk bbbs ssss cccc cccc cccc cccc
    "CY": u"(CY)" + CK + N4 + N4 + C4 + C4 + C4 + C4,
    # Czech Republic    (20n)   CZkk bbbb ssss sscc cccc cccc
    "CZ": u"(CZ)" + CK + N4 + N4 + N4 + N4 + N4,
    # Denmark   (14n)   DKkk bbbb cccc cccc cc
    "DK": u"(DK)" + CK + N4 + N4 + N4 + N2,
    # Dominican Republic    (4a,20n)    DOkk bbbb cccc cccc cccc cccc cccc
    "DO": u"(DO)" + CK + A4 + N4 + N4 + N4 + N4 + N4,
    # EAt Timor    (19n) TLkk bbbc cccc cccc cccc cxx
    "TL": u"(TL)" + CK + N4 + N4 + N4 + N4 + N3,
    # Estonia   (16n) EEkk bbss cccc cccc cccx
    "EE": u"(EE)" + CK + N4 + N4 + N4 + N4,
    # Faroe Islands    (14n) FOkk bbbb cccc cccc cx
    "FO": u"(FO)" + CK + N4 + N4 + N4 + N2,
    # Finland   (14n) FIkk bbbb bbcc cccc cx
    "FI": u"(FI)" + CK + N4 + N4 + N4 + N2,
    # France    (10n,11c,2n) FRkk bbbb bsss sscc cccc cccc cxx
    "FR": u"(FR)" + CK + N4 + N4 + N2 + C2 + C4 + C4 + C + N2,
    # Georgia   (2c,16n)  GEkk bbcc cccc cccc cccc cc
    "GE": u"(GE)" + CK + C2 + N2 + N4 + N4 + N4 + N2,
    # Germany   (18n) DEkk bbbb bbbb cccc cccc cc
    "DE": u"(DE)" + CK + N4 + N4 + N4 + N4 + N2,
    # Gibraltar (4a,15c)  GIkk bbbb cccc cccc cccc ccc
    "GI": u"(GI)" + CK + A4 + C4 + C4 + C4 + C3,
    # Greece    (7n,16c)  GRkk bbbs sssc cccc cccc cccc ccc
    "GR": u"(GR)" + CK + N4 + N3 + C + C4 + C4 + C4 + C3,
    # Greenland     (14n) GLkk bbbb cccc cccc cc
    "GL": u"(GL)" + CK + N4 + N4 + N4 + N2,
    # Guatemala (4c,20c)  GTkk bbbb mmtt cccc cccc cccc cccc
    "GT": u"(GT)" + CK + C4 + C4 + C4 + C4 + C4 + C4,
    # Hungary   (24n) HUkk bbbs sssx cccc cccc cccc cccx
    "HU": u"(HU)" + CK + N4 + N4 + N4 + N4 + N4 + N4,
    # Iceland   (22n) ISkk bbbb sscc cccc iiii iiii ii
    "IS": u"(IS)" + CK + N4 + N4 + N4 + N4 + N4 + N2,
    # Ireland   (4c,14n)  IEkk aaaa bbbb bbcc cccc cc
    "IE": u"(IE)" + CK + C4 + N4 + N4 + N4 + N2,
    # Israel (19n) ILkk bbbn nncc cccc cccc ccc
    "IL": u"(IL)" + CK + N4 + N4 + N4 + N4 + N3,
    # Italy (1a,10n,12c)  ITkk xbbb bbss sssc cccc cccc ccc
    "IT": u"(IT)" + CK + A + N3 + N4 + N3 + C + C3 + C + C4 + C3,
    # Jordan    (4a,22n)  JOkk bbbb ssss cccc cccc cccc cccc cc
    "JO": u"(JO)" + CK + A4 + N4 + N4 + N4 + N4 + N4 + N2,
    # Kazakhstan    (3n,13c)  KZkk bbbc cccc cccc cccc
    "KZ": u"(KZ)" + CK + N3 + C + C4 + C4 + C4,
    # Kosovo    (4n,10n,2n)   XKkk bbbb cccc cccc cccc
    "XK": u"(XK)" + CK + N4 + N4 + N4 + N4,
    # Kuwait    (4a,22c)  KWkk bbbb cccc cccc cccc cccc cccc cc
    "KW": u"(KW)" + CK + A4 + C4 + C4 + C4 + C4 + C4 + C2,
    # Latvia    (4a,13c)  LVkk bbbb cccc cccc cccc c
    "LV": u"(LV)" + CK + A4 + C4 + C4 + C4 + C,
    # Lebanon   (4n,20c)  LBkk bbbb cccc cccc cccc cccc cccc
    "LB": u"(LB)" + CK + N4 + C4 + C4 + C4 + C4 + C4,
    # LiechteNtein (5n,12c)  LIkk bbbb bccc cccc cccc c
    "LI": u"(LI)" + CK + N4 + N + C3 + C4 + C4 + C,
    # Lithuania (16n) LTkk bbbb bccc cccc cccc
    "LT": u"(LT)" + CK + N4 + N4 + N4 + N4,
    # Luxembourg    (3n,13c)  LUkk bbbc cccc cccc cccc
    "LU": u"(LU)" + CK + N3 + C + C4 + C4 + C4,
    # Malta (4a,5n,18c)   MTkk bbbb ssss sccc cccc cccc cccc ccc
    "MT": u"(MT)" + CK + A4 + N4 + N + C3 + C4 + C4 + C4 + C3,
    # Mauritania    (23n) MRkk bbbb bsss sscc cccc cccc cxx
    "MR": u"(MR)" + CK + N4 + N4 + N4 + N4 + N4 + N3,
    # Mauritius (4a,19n,3a)   MUkk bbbb bbss cccc cccc cccc 000m mm
    "MU": u"(MU)" + CK + A4 + N4 + N4 + N4 + N4 + N3 + A,
    # Moldova   (2c,18c)  MDkk bbcc cccc cccc cccc cccc
    "MD": u"(MD)" + CK + C4 + C4 + C4 + C4 + C4,
    # Monaco    (10n,11c,2n)  MCkk bbbb bsss sscc cccc cccc cxx
    "MC": u"(MC)" + CK + N4 + N4 + N2 + C2 + C4 + C4 + C + N2,
    # Montenegro    (18n) MEkk bbbc cccc cccc cccc xx
    "ME": u"(ME)" + CK + N4 + N4 + N4 + N4 + N2,
    # Netherlands   (4a,10n)  NLkk bbbb cccc cccc cc
    "NL": u"(NL)" + CK + A4 + N4 + N4 + N2,
    # North Macedonia   (3n,10c,2n)   MKkk bbbc cccc cccc cxx
    "MK": u"(MK)" + CK + N3 + C + C4 + C4 + C + N2,
    # Norway    (11n) NOkk bbbb cccc ccx
    "NO": u"(NO)" + CK + N4 + N4 + N3,
    # Pakistan  (4c,16n)  PKkk bbbb cccc cccc cccc cccc
    "PK": u"(PK)" + CK + C4 + N4 + N4 + N4 + N4,
    # Palestinian territories   (4c,21n)  PSkk bbbb xxxx xxxx xccc cccc cccc c
    "PS": u"(PS)" + CK + C4 + N4 + N4 + N4 + N4 + N,
    # Poland    (24n) PLkk bbbs sssx cccc cccc cccc cccc
    "PL": u"(PL)" + CK + N4 + N4 + N4 + N4 + N4 + N4,
    # Portugal  (21n) PTkk bbbb ssss cccc cccc cccx x
    "PT": u"(PT)" + CK + N4 + N4 + N4 + N4 + N,
    # Qatar (4a,21c)  QAkk bbbb cccc cccc cccc cccc cccc c
    "QA": u"(QA)" + CK + A4 + C4 + C4 + C4 + C4 + C,
    # Romania   (4a,16c)  ROkk bbbb cccc cccc cccc cccc
    "RO": u"(RO)" + CK + A4 + C4 + C4 + C4 + C4,
    # San Marino    (1a,10n,12c)  SMkk xbbb bbss sssc cccc cccc ccc
    "SM": u"(SM)" + CK + A + N3 + N4 + N3 + C + C4 + C4 + C3,
    # Saudi Arabia  (2n,18c)  SAkk bbcc cccc cccc cccc cccc
    "SA": u"(SA)" + CK + N2 + C2 + C4 + C4 + C4 + C4,
    # Serbia    (18n) RSkk bbbc cccc cccc cccc xx
    "RS": u"(RS)" + CK + N4 + N4 + N4 + N4 + N2,
    # Slovakia  (20n) SKkk bbbb ssss sscc cccc cccc
    "SK": u"(SK)" + CK + N4 + N4 + N4 + N4 + N4,
    # Slovenia  (15n) SIkk bbss sccc cccc cxx
    "SI": u"(SI)" + CK + N4 + N4 + N4 + N3,
    # Spain (20n) ESkk bbbb ssss xxcc cccc cccc
    "ES": u"(ES)" + CK + N4 + N4 + N4 + N4 + N4,
    # Sweden    (20n) SEkk bbbc cccc cccc cccc cccc
    "SE": u"(SE)" + CK + N4 + N4 + N4 + N4 + N4,
    # Switzerland   (5n,12c)  CHkk bbbb bccc cccc cccc c
    "CH": u"(CH)" + CK + N4 + N + C3 + C4 + C4 + C,
    # Tunisia   (20n) TNkk bbss sccc cccc cccc cccc
    "TN": u"(TN)" + CK + N4 + N4 + N4 + N4 + N4,
    # Turkey    (5n,17c)  TRkk bbbb bxcc cccc cccc cccc cc
    "TR": u"(TR)" + CK + N4 + N + C3 + C4 + C4 + C4 + C2,
    # United Arab Emirates  (3n,16n)  AEkk bbbc cccc cccc cccc ccc
    "AE": u"(AE)" + CK + N4 + N4 + N4 + N4 + N3,
    # United Kingdom (4a,14n) GBkk bbbb ssss sscc cccc cc
    "GB": u"(GB)" + CK + A4 + N4 + N4 + N4 + N2,
    # Vatican City  (3n,15n)  VAkk bbbc cccc cccc cccc cc
    "VA": u"(VA)" + CK + N4 + N4 + N4 + N4 + N2,
    # Virgin Islands, British   (4c,16n)  VGkk bbbb cccc cccc cccc cccc
    "VG": u"(VG)" + CK + C4 + N4 + N4 + N4 + N4,
}
