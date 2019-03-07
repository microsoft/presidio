from unittest import TestCase
import string

from assertions import assert_result
from analyzer.predefined_recognizers.iban_recognizer import IbanRecognizer, IBAN_GENERIC_SCORE, LETTERS
from analyzer.entity_recognizer import EntityRecognizer

iban_recognizer = IbanRecognizer()
entities = ["IBAN_CODE"]

def update_iban_checksum(iban):
    '''
    Generates an IBAN, with checksum digits
    This is based on: https://www.ibantest.com/en/how-is-the-iban-check-digit-calculated
    '''
    iban_no_spaces = iban.replace(' ', '')
    iban_digits = (iban_no_spaces[4:] +iban_no_spaces[:2] + '00').upper().translate(LETTERS)
    check_digits = '{:0>2}'.format(98 - (int(iban_digits) % 97))
    return iban[:2] + check_digits + iban[4:]
    

class TestIbanRecognizer(TestCase):
# Test valid and invalid ibans per each country which supports IBAN - without context
    #Albania (8n, 16c) ALkk bbbs sssx cccc cccc cccc cccc
    def test_AL_iban_valid_no_spaces(self):
        iban = 'AL47212110090000000235698741'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 28, EntityRecognizer.MAX_SCORE)

    def test_AL_iban_valid_with_spaces(self):
        iban = 'AL47 2121 1009 0000 0002 3569 8741'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 34, EntityRecognizer.MAX_SCORE)
    
    def test_AL_iban_invalid_format_valid_checksum(self):
        iban = 'AL47 212A 1009 0000 0002 3569 8741'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0
    
    def test_AL_iban_invalid_length(self):
        iban = 'AL47 212A 1009 0000 0002 3569 874'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0
    
    def test_AL_iban_invalid_checksum(self):
        iban = 'AL47 2121 1009 0000 0002 3569 8740'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0
   
    #Andorra (8n, 12c) ADkk bbbs sssx cccc cccc cccc
    def test_AD_valid_iban_no_spaces(self):
        iban = 'AD1200012030200359100100'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 24, EntityRecognizer.MAX_SCORE)

    def test_AD_iban_valid_with_spaces(self):
        iban = 'AD12 0001 2030 2003 5910 0100'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 29, EntityRecognizer.MAX_SCORE)

    def test_AD_iban_invalid_format_valid_checksum(self):
        iban = 'AD12000A2030200359100100'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0
    
    def test_AD_iban_invalid_length(self):
        iban = 'AD12000A203020035910010'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    def test_AD_iban_invalid_checksum(self):
        iban = 'AD12 0001 2030 2003 5910 0101'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0
    
    # Austria (16n) ATkk bbbb bccc cccc cccc
    def test_AT_iban_valid_no_spaces(self):
        iban = 'AT611904300234573201'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 20, EntityRecognizer.MAX_SCORE)

    def test_AT_iban_valid_with_spaces(self):
        iban = 'AT61 1904 3002 3457 3201'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 24, EntityRecognizer.MAX_SCORE)
    
    def test_AT_iban_invalid_format_valid_checksum(self):
        iban = 'AT61 1904 A002 3457 3201'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0
    
    def test_AT_iban_invalid_length(self):
        iban = 'AT61 1904 3002 3457 320'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0
    
    def test_AT_iban_invalid_checksum(self):
        iban = 'AT61 1904 3002 3457 3202'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0
    
    # Azerbaijan    (4c,20n) AZkk bbbb cccc cccc cccc cccc cccc
    def test_AZ_iban_valid_no_spaces(self):
        iban = 'AZ21NABZ00000000137010001944'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 28, EntityRecognizer.MAX_SCORE)

    def test_AZ_iban_valid_with_spaces(self):
        iban = 'AZ21 NABZ 0000 0000 1370 1000 1944'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 34, EntityRecognizer.MAX_SCORE)

    def test_AZ_iban_invalid_format_valid_checksum(self):
        iban = 'AZ21NABZ000000001370100019'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0
    
    def test_AZ_iban_invalid_length(self):
        iban = 'AZ21NABZ0000000013701000194'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    def test_AZ_iban_invalid_checksum(self):
        iban = 'AZ21NABZ00000000137010001945'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Bahrain   (4a,14c)    BHkk bbbb cccc cccc cccc cc
    def test_BH_iban_valid_no_spaces(self):
        iban = 'BH67BMAG00001299123456'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 22, EntityRecognizer.MAX_SCORE)

    def testBH_iban_valid__with_spaces(self):
        iban = 'BH67 BMAG 0000 1299 1234 56'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 27, EntityRecognizer.MAX_SCORE)
    
    def test_BH_iban_invalid_format_valid_checksum(self):
        iban = 'BH67BMA100001299123456'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0
    
    def test_BH_iban_invalid_length(self):
        iban = 'BH67BMAG0000129912345'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    def test_BH_iban_invalid_checksum(self):
        iban = 'BH67BMAG00001299123457'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0
    
    # Belarus (4c, 4n, 16c)   BYkk bbbb aaaa cccc cccc cccc cccc  
    def test_BY_iban_valid_no_spaces(self):
        iban = 'BY13NBRB3600900000002Z00AB00'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 28, EntityRecognizer.MAX_SCORE)

    def test_BY_iban_valid_with_spaces(self):
        iban = 'BY13 NBRB 3600 9000 0000 2Z00 AB00'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 34, EntityRecognizer.MAX_SCORE)
    
    def test_BY_iban_invalid_format_valid_checksum(self):
        iban = 'BY13NBRBA600900000002Z00AB00'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0
    
    def test_BY_iban_invalid_length(self):
        iban = 'BY13 NBRB 3600 9000 0000 2Z00 AB0'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0
    
    def test_BY_iban_invalid_checksum(self):
        iban = 'BY13NBRB3600900000002Z00AB01'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Belgium (12n)   BEkk bbbc cccc ccxx 
    def test_BE_iban_valid_no_spaces(self):
        iban = 'BE68539007547034'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 16, EntityRecognizer.MAX_SCORE)

    def test_BE_iban_valid_with_spaces(self):
        iban = 'BE71 0961 2345 6769'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 19, EntityRecognizer.MAX_SCORE)
    
    def test_BE_iban_invalid_format_valid_checksum(self):
        iban = 'BE71 A961 2345 6769'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0
    
    def test_BE_iban_invalid_length(self):
        iban = 'BE6853900754703'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    def test_BE_iban_invalid_checksum(self):
        iban = 'BE71 0961 2345 6760'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0
    
    # Bosnia and Herzegovina    (16n)   BAkk bbbs sscc cccc ccxx
    def test_BA_iban_valid_no_spaces(self):
        iban = 'BA391290079401028494'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 20, EntityRecognizer.MAX_SCORE)

    def test_BA_iban_valid_with_spaces(self):
        iban = 'BA39 1290 0794 0102 8494'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 24, EntityRecognizer.MAX_SCORE)

    def test_BA_iban_invalid_format_valid_checksum(self):
        iban = 'BA39 A290 0794 0102 8494'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0
    
    def test_BA_iban_invalid_length(self):
        iban = 'BA39129007940102849'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    def test_BA_iban_invalid_checksum(self):
        iban = 'BA39 1290 0794 0102 8495'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Brazil (23n,1a,1c) BRkk bbbb bbbb ssss sccc cccc ccct n
    def test_BR_iban_valid_no_spaces(self):
        iban = 'BR9700360305000010009795493P1'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 29, EntityRecognizer.MAX_SCORE)

    def test_BR_iban_valid_with_spaces(self):
        iban = 'BR97 0036 0305 0000 1000 9795 493P 1'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 36, EntityRecognizer.MAX_SCORE)
    
    def test_BR_iban_invalid_format_valid_checksum(self):
        iban = 'BR97 0036 A305 0000 1000 9795 493P 1'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0
    
    def test_BR_iban_invalid_length(self):
        iban = 'BR9700360305000010009795493P'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0
    
    def test_BR_iban_invalid_checksum(self):
        iban = 'BR97 0036 0305 0000 1000 9795 493P 2'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Bulgaria  (4a,6n,8c)  BGkk bbbb ssss ttcc cccc cc
    def test_BG_iban_valid_no_spaces(self):
        iban = 'BG80BNBG96611020345678'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 22, EntityRecognizer.MAX_SCORE)

    def test_BG_iban_valid_with_spaces(self):
        iban = 'BG80 BNBG 9661 1020 3456 78'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 27, EntityRecognizer.MAX_SCORE)
    
    def test_BG_iban_invalid_format_valid_checksum(self):
        iban = 'BG80 BNBG 9661 A020 3456 78'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0
    
    def test_BG_iban_invalid_length(self):
        iban = 'BG80BNBG9661102034567'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    def test_BG_iban_invalid_checksum(self):
        iban = 'BG80 BNBG 9661 1020 3456 79'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Costa Rica    (18n)   CRkk 0bbb cccc cccc cccc cc 0 = always zero
    def test_CR_iban_valid_no_spaces(self):
        iban = 'CR05015202001026284066'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 22, EntityRecognizer.MAX_SCORE)

    def test_CR_iban_valid_with_spaces(self):
        iban = 'CR05 0152 0200 1026 2840 66'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 27, EntityRecognizer.MAX_SCORE)
    
    def test_CR_iban_invalid_format_valid_checksum(self):
        iban = 'CR05 0152 0200 1026 2840 6A'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0
    
    def test_CR_iban_invalid_length(self):
        iban = 'CR05 0152 0200 1026 2840 6'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0
    
    def test_CR_iban_invalid_checksum(self):
        iban = 'CR05 0152 0200 1026 2840 67'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Croatia   (17n)   HRkk bbbb bbbc cccc cccc c  
    def test_HR_iban_valid_no_spaces(self):
        iban = 'HR1210010051863000160'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 21, EntityRecognizer.MAX_SCORE)

    def test_HR_iban_valid_with_spaces(self):
        iban = 'HR12 1001 0051 8630 0016 0'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 26, EntityRecognizer.MAX_SCORE)
    
    def test_HR_iban_invalid_format_valid_checksum(self):
        iban = 'HR12 001 0051 8630 0016 A'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    def test_HR_iban_invalid_length(self):
        iban = 'HR121001005186300016'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0
    
    def test_HR_iban_invalid_Checksum(self):
        iban = 'HR12 1001 0051 8630 0016 1'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Cyprus    (8n,16c)  CYkk bbbs ssss cccc cccc cccc cccc
    def test_CY_iban_valid_no_spaces(self):
        iban = 'CY17002001280000001200527600'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 28, EntityRecognizer.MAX_SCORE)

    def test_CY_iban_valid_with_spaces(self):
        iban = 'CY17 0020 0128 0000 0012 0052 7600'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 34, EntityRecognizer.MAX_SCORE)
    
    def test_CY_iban_invalid_format_valid_checksum(self):
        iban = 'CY17 0020 A128 0000 0012 0052 7600'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0
    
    def test_CY_iban_invalid_length(self):
        iban = 'CY17 0020 0128 0000 0012 0052 760'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    def test_CY_iban_invalid_checksum(self):
        iban = 'CY17 0020 0128 0000 0012 0052 7601'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Czech Republic    (20n)   CZkk bbbb ssss sscc cccc cccc
    def test_CZ_iban_valid_no_spaces(self):
        iban = 'CZ6508000000192000145399'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 24, EntityRecognizer.MAX_SCORE)

    def test_CZ_iban_valid_with_spaces(self):
        iban = 'CZ65 0800 0000 1920 0014 5399'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 29, EntityRecognizer.MAX_SCORE)
    
    def test_CZ_iban_invalid_format_valid_checksum(self):
        iban = 'CZ65 0800 A000 1920 0014 5399'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0
    
    def test_CZ_iban_invalid_length(self):
        iban = 'CZ65 0800 0000 1920 0014 539'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    def test_CZ_iban_invalid_checksum(self):
        iban = 'CZ65 0800 0000 1920 0014 5390'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Denmark   (14n)   DKkk bbbb cccc cccc cc
    def test_DK_iban_valid_no_spaces(self):
        iban = 'DK5000400440116243'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 18, EntityRecognizer.MAX_SCORE)

    def test_DK_iban_valid_with_spaces(self):
        iban = 'DK50 0040 0440 1162 43'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 22, EntityRecognizer.MAX_SCORE)
    
    def test_DK_iban_invalid_format_valid_checksum(self):
        iban = 'DK50 0040 A440 1162 43'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0
    
    def test_DK_iban_invalid_length(self):
        iban = 'DK50 0040 0440 1162 4'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0
    
    def test_DK_iban_invalid_checksum(self):
        iban = 'DK50 0040 0440 1162 44'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Dominican Republic    (4a,20n)    DOkk bbbb cccc cccc cccc cccc cccc
    def test_DO_iban_valid_no_spaces(self):
        iban = 'DO28BAGR00000001212453611324'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 28, EntityRecognizer.MAX_SCORE)

    def test_DO_iban_valid_with_spaces(self):
        iban = 'DO28 BAGR 0000 0001 2124 5361 1324'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 34, EntityRecognizer.MAX_SCORE)
    
    def test_DO_iban_invalid_format_valid_checksum(self):
        iban = 'DO28 BAGR A000 0001 2124 5361 1324'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0
    
    def test_DO_iban_invalid_length(self):
        iban = 'DO28 BAGR 0000 0001 2124 5361 132'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    def test_DO_iban_invalid_checksum(self):
        iban = 'DO28 BAGR 0000 0001 2124 5361 1325'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # East Timor (Timor-Leste)   (19n) TLkk bbbc cccc cccc cccc cxx
    def test_TL_iban_valid_no_spaces(self):
        iban = 'TL380080012345678910157'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 23, EntityRecognizer.MAX_SCORE)

    def test_TL_iban_valid_with_spaces(self):
        iban = 'TL38 0080 0123 4567 8910 157'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 28, EntityRecognizer.MAX_SCORE)
    
    def test_TL_iban_invalid_format_valid_checksum(self):
        iban = 'TL38 A080 0123 4567 8910 157'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0
    
    def test_TL_iban_invalid_checksum(self):
        iban = 'TL38 0080 0123 4567 8910 158'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Estonia   (16n) EEkk bbss cccc cccc cccx  
    def test_EE_iban_valid_no_spaces(self):
        iban = 'EE382200221020145685'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 20, EntityRecognizer.MAX_SCORE)

    def test_EE_iban_valid_with_spaces(self):
        iban = 'EE38 2200 2210 2014 5685'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 24, EntityRecognizer.MAX_SCORE)
    
    def test_EE_iban_invalid_format_valid_checksum(self):
        iban = 'EE38 A200 2210 2014 5685'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0
    
    def test_EE_iban_invalid_checksum(self):
        iban = 'EE38 2200 2210 2014 5686'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Faroe Islands (14n) FOkk bbbb cccc cccc cx 
    def test_FO_iban_valid_no_spaces(self):
        iban = 'FO6264600001631634'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 18, EntityRecognizer.MAX_SCORE)

    def test_FO_iban_valid_with_spaces(self):
        iban = 'FO62 6460 0001 6316 34'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 22, EntityRecognizer.MAX_SCORE)
    
    def test_FO_iban_invalid_format_valid_checksum(self):
        iban = 'FO62 A460 0001 6316 34'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0
    
    def test_FO_iban_invalid_checksum(self):
        iban = 'FO62 6460 0001 6316 35'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Finland   (14n) FIkk bbbb bbcc cccc cx  
    def test_FI_iban_valid_no_spaces(self):
        iban = 'FI2112345600000785'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 18, EntityRecognizer.MAX_SCORE)

    def test_FI_iban_valid_with_spaces(self):
        iban = 'FI21 1234 5600 0007 85'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 22, EntityRecognizer.MAX_SCORE)

    def test_FI_iban_invalid_format_valid_checksum(self):
        iban = 'FI21 A234 5600 0007 85'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0
    
    def test_FI_iban_invalid_checksum(self):
        iban = 'FI21 1234 5600 0007 86'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # France    (10n,11c,2n) FRkk bbbb bsss sscc cccc cccc cxx  
    def test_FR_iban_valid_no_spaces(self):
        iban = 'FR1420041010050500013M02606'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 27, EntityRecognizer.MAX_SCORE)

    def test_FR_iban_valid_with_spaces(self):
        iban = 'FR14 2004 1010 0505 0001 3M02 606'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 33, EntityRecognizer.MAX_SCORE)
    
    def test_FR_iban_invalid_format_valid_checksum(self):
        iban = 'FR14 A004 1010 0505 0001 3M02 606'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0
    
    def test_FR_iban_invalid_checksum(self):
        iban = 'FR14 2004 1010 0505 0001 3M02 607'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Georgia   (2c,16n)  GEkk bbcc cccc cccc cccc cc
    def test_GE_iban_valid_no_spaces(self):
        iban = 'GE29NB0000000101904917'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 22, EntityRecognizer.MAX_SCORE)

    def test_GE_iban_valid_with_spaces(self):
        iban = 'GE29 NB00 0000 0101 9049 17'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 27, EntityRecognizer.MAX_SCORE)
    
    def test_GE_iban_invalid_format_valid_checksum(self):
        iban = 'GE29 NBA0 0000 0101 9049 17'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0
    
    def test_GE_iban_invalid_checksum(self):
        iban = 'GE29 NB00 0000 0101 9049 18'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Germany   (18n) DEkk bbbb bbbb cccc cccc cc
    def test_DE_iban_valid_no_spaces(self):
        iban = 'DE89370400440532013000'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 22, EntityRecognizer.MAX_SCORE)

    def test_DE_iban_valid_with_spaces(self):
        iban = 'DE89 3704 0044 0532 0130 00'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 27, EntityRecognizer.MAX_SCORE)
    
    def test_DE_iban_invalid_format_valid_checksum(self):
        iban = 'DE89 A704 0044 0532 0130 00'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0
    
    def test_DE_iban_invalid_checksum(self):
        iban = 'DE89 3704 0044 0532 0130 01'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Gibraltar (4a,15c)  GIkk bbbb cccc cccc cccc ccc
    def test_GI_iban_valid_no_spaces(self):
        iban = 'GI75NWBK000000007099453'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 23, EntityRecognizer.MAX_SCORE)

    def test_GI_iban_valid_with_spaces(self):
        iban = 'GI75 NWBK 0000 0000 7099 453'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 28, EntityRecognizer.MAX_SCORE)
  
    def test_GI_iban_invalid_format_valid_checksum(self):
        iban = 'GI75 aWBK 0000 0000 7099 453'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 28, IBAN_GENERIC_SCORE)


    def test_GI_iban_invalid_checksum(self):
        iban = 'GI75 NWBK 0000 0000 7099 454'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Greece    (7n,16c)  GRkk bbbs sssc cccc cccc cccc ccc
    def test_GR_iban_valid_no_spaces(self):
        iban = 'GR1601101250000000012300695'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 27, EntityRecognizer.MAX_SCORE)

    def test_GR_iban_valid_with_spaces(self):
        iban = 'GR16 0110 1250 0000 0001 2300 695'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 33, EntityRecognizer.MAX_SCORE)
    
    def test_GR_iban_invalid_format_valid_checksum(self):
        iban = 'GR16 A110 1250 0000 0001 2300 695'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0
    
    def test_GR_iban_invalid_checksum(self):
        iban = 'GR16 0110 1250 0000 0001 2300 696'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Greenland (14n) GLkk bbbb cccc cccc cc 
    def test_GL_iban_valid_no_spaces(self):
        iban = 'GL8964710001000206'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 18, EntityRecognizer.MAX_SCORE)

    def test_GL_iban_valid_with_spaces(self):
        iban = 'GL89 6471 0001 0002 06'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 22, EntityRecognizer.MAX_SCORE)
    
    def test_GL_iban_invalid_format_valid_checksum(self):
        iban = 'GL89 A471 0001 0002 06'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0
    
    def test_GL_iban_invalid_checksum(self):
        iban = 'GL89 6471 0001 0002 07'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Guatemala (4c,20c)  GTkk bbbb mmtt cccc cccc cccc cccc
    def test_GT_iban_valid_no_spaces(self):
        iban = 'GT82TRAJ01020000001210029690'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 28, EntityRecognizer.MAX_SCORE)

    def test_GT_iban_valid_with_spaces(self):
        iban = 'GT82 TRAJ 0102 0000 0012 1002 9690'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 34, EntityRecognizer.MAX_SCORE)
    
    def test_GT_iban_invalid_format_valid_checksum(self):
        iban = 'GT82 TRAJ 0102 0000 0012 1002 9690 A'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0
    
    def test_GT_iban_invalid_checksum(self):
        iban = 'GT82 TRAJ 0102 0000 0012 1002 9691'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Hungary   (24n) HUkk bbbs sssx cccc cccc cccc cccx
    def test_HU_iban_valid_no_spaces(self):
        iban = 'HU42117730161111101800000000'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 28, EntityRecognizer.MAX_SCORE)

    def test_HU_iban_valid_with_spaces(self):
        iban = 'HU42 1177 3016 1111 1018 0000 0000'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 34, EntityRecognizer.MAX_SCORE)
    
    def test_HU_iban_invalid_format_valid_checksum(self):
        iban = 'HU42 A177 3016 1111 1018 0000 0000'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0
    
    def test_HU_iban_invalid_checksum(self):
        iban = 'HU42 1177 3016 1111 1018 0000 0001'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Iceland   (22n) ISkk bbbb sscc cccc iiii iiii ii
    def test_IS_iban_valid_no_spaces(self):
        iban = 'IS140159260076545510730339'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 26, EntityRecognizer.MAX_SCORE)

    def test_IS_iban_valid_with_spaces(self):
        iban = 'IS14 0159 2600 7654 5510 7303 39'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 32, EntityRecognizer.MAX_SCORE)
    
    def test_IS_iban_invalid_format_valid_checksum(self):
        iban = 'IS14 A159 2600 7654 5510 7303 39'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0
    
    def test_IS_iban_invalid_checksum(self):
        iban = 'IS14 0159 2600 7654 5510 7303 30'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Ireland   (4c,14n)  IEkk aaaa bbbb bbcc cccc cc
    def test_IE_iban_valid_no_spaces(self):
        iban = 'IE29AIBK93115212345678'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 22, EntityRecognizer.MAX_SCORE)

    def test_IE_iban_valid_with_spaces(self):
        iban = 'IE29 AIBK 9311 5212 3456 78'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 27, EntityRecognizer.MAX_SCORE)
    
    def test_IE_iban_invalid_format_valid_checksum(self):
        iban = 'IE29 AIBK A311 5212 3456 78'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0
    
    def test_IE_iban_invalid_checksum(self):
        iban = 'IE29 AIBK 9311 5212 3456 79'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Israel (19n)   ILkk bbbn nncc cccc cccc ccc
    def test_IL_iban_valid_no_spaces(self):
        iban = 'IL620108000000099999999'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 23, EntityRecognizer.MAX_SCORE)

    def test_IL_iban_valid_with_spaces(self):
        iban = 'IL62 0108 0000 0009 9999 999'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 28, EntityRecognizer.MAX_SCORE)
    
    def test_IL_iban_invalid_format_valid_checksum(self):
        iban = 'IL62 A108 0000 0009 9999 999'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    def test_IL_iban_valid_checksum(self):
        iban = 'IL62 0108 0000 0009 9999 990'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Italy (1a,10n,12c)  ITkk xbbb bbss sssc cccc cccc ccc
    def test_IT_iban_valid_no_spaces(self):
        iban = 'IT60X0542811101000000123456'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 27, EntityRecognizer.MAX_SCORE)

    def test_IT_iban_valid_with_spaces(self):
        iban = 'IT60 X054 2811 1010 0000 0123 456'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 33, EntityRecognizer.MAX_SCORE)
    
    def test_IT_iban_invalid_format_valid_checksum(self):
        iban = 'IT60 XW54 2811 1010 0000 0123 456'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    def test_IT_iban_valid_checksum(self):
        iban = 'IT60 X054 2811 1010 0000 0123 457'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Jordan    (4a,22n)  JOkk bbbb ssss cccc cccc cccc cccc cc
    def test_JO_iban_valid_no_spaces(self):
        iban = 'JO94CBJO0010000000000131000302'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 30, EntityRecognizer.MAX_SCORE)

    def test_JO_iban_valid_with_spaces(self):
        iban = 'JO94 CBJO 0010 0000 0000 0131 0003 02'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 37, EntityRecognizer.MAX_SCORE)
    
    def test_JO_iban_invalid_format_valid_checksum(self):
        iban = 'JO94 CBJO A010 0000 0000 0131 0003 02'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    def test_JO_iban_valid_checksum(self):
        iban = 'JO94 CBJO 0010 0000 0000 0131 0003 03'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Kazakhstan    (3n,13c)  KZkk bbbc cccc cccc cccc
    def test_KZ_iban_valid_no_spaces(self):
        iban = 'KZ86125KZT5004100100'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 20, EntityRecognizer.MAX_SCORE)

    def test_KZ_iban_valid_with_spaces(self):
        iban = 'KZ86 125K ZT50 0410 0100'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 24, EntityRecognizer.MAX_SCORE)
    
    def test_KZ_iban_invalid_format_valid_checksum(self):
        iban = 'KZ86 A25K ZT50 0410 0100'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    def test_KZ_iban_valid_checksum(self):
        iban = 'KZ86 125K ZT50 0410 0101'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Kosovo    (4n,10n,2n)   XKkk bbbb cccc cccc cccc
    def test_XK_iban_valid_no_spaces(self):
        iban = 'XK051212012345678906'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 20, EntityRecognizer.MAX_SCORE)

    def test_XK_iban_valid_with_spaces(self):
        iban = 'XK05 1212 0123 4567 8906'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 24, EntityRecognizer.MAX_SCORE)
    
    def test_XK_iban_invalid_format_valid_checksum(self):
        iban = 'XK05 A212 0123 4567 8906'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    def test_XK_iban_valid_checksum(self):
        iban = 'XK05 1212 0123 4567 8907'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Kuwait    (4a,22c)  KWkk bbbb cccc cccc cccc cccc cccc cc
    def test_KW_iban_valid_no_spaces(self):
        iban = 'KW81CBKU0000000000001234560101'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 30, EntityRecognizer.MAX_SCORE)

    def test_KW_iban_valid_with_spaces(self):
        iban = 'KW81 CBKU 0000 0000 0000 1234 5601 01'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 37, EntityRecognizer.MAX_SCORE)
    
    def test_KW_iban_invalid_format_valid_checksum(self):
        iban = 'KW81 aBKU 0000 0000 0000 1234 5601 01'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 37, IBAN_GENERIC_SCORE)


    def test_KW_iban_valid_checksum(self):
        iban = 'KW81 CBKU 0000 0000 0000 1234 5601 02'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Latvia    (4a,13c)  LVkk bbbb cccc cccc cccc c
    def test_LV_iban_valid_no_spaces(self):
        iban = 'LV80BANK0000435195001'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 21, EntityRecognizer.MAX_SCORE)

    def test_LV_iban_valid_with_spaces(self):
        iban = 'LV80 BANK 0000 4351 9500 1'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 26, EntityRecognizer.MAX_SCORE)
    
    def test_LV_iban_invalid_format_valid_checksum(self):
        iban = 'LV80 bANK 0000 4351 9500 1'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 26, IBAN_GENERIC_SCORE)

    def test_LV_iban_valid_checksum(self):
        iban = 'LV80 BANK 0000 4351 9500 2'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Lebanon   (4n,20c)  LBkk bbbb cccc cccc cccc cccc cccc
    def test_LB_iban_valid_no_spaces(self):
        iban = 'LB62099900000001001901229114'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 28, EntityRecognizer.MAX_SCORE)

    def test_LB_iban_valid_with_spaces(self):
        iban = 'LB62 0999 0000 0001 0019 0122 9114'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 34, EntityRecognizer.MAX_SCORE)
    
    def test_LB_iban_invalid_format_valid_checksum(self):
        iban = 'LB62 A999 0000 0001 0019 0122 9114'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    def test_LB_iban_valid_checksum(self):
        iban = 'LB62 0999 0000 0001 0019 0122 9115'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Liechtenstein (5n,12c)  LIkk bbbb bccc cccc cccc c
    def test_LI_iban_valid_no_spaces(self):
        iban = 'LI21088100002324013AA'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 21, EntityRecognizer.MAX_SCORE)

    def test_LI_iban_valid_with_spaces(self):
        iban = 'LI21 0881 0000 2324 013A A'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 26, EntityRecognizer.MAX_SCORE)
    
    def test_LI_iban_invalid_format_valid_checksum(self):
        iban = 'LI21 A881 0000 2324 013A A'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    def test_LI_iban_valid_checksum(self):
        iban = 'LI21 0881 0000 2324 013A B'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Lithuania (16n) LTkk bbbb bccc cccc cccc
    def test_LT_iban_valid_no_spaces(self):
        iban = 'LT121000011101001000'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 20, EntityRecognizer.MAX_SCORE)

    def test_LT_iban_valid_with_spaces(self):
        iban = 'LT12 1000 0111 0100 1000'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 24, EntityRecognizer.MAX_SCORE)
    
    def test_LT_iban_invalid_format_valid_checksum(self):
        iban = 'LT12 A000 0111 0100 1000'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    def test_LT_iban_valid_checksum(self):
        iban = 'LT12 1000 0111 0100 1001'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Luxembourg    (3n,13c)  LUkk bbbc cccc cccc cccc
    def test_LU_iban_valid_no_spaces(self):
        iban = 'LU280019400644750000'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 20, EntityRecognizer.MAX_SCORE)

    def test_LU_iban_valid_with_spaces(self):
        iban = 'LU28 0019 4006 4475 0000'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 24, EntityRecognizer.MAX_SCORE)
    
    def test_LU_iban_invalid_format_valid_checksum(self):
        iban = 'LU28 A019 4006 4475 0000'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    def test_LU_iban_valid_checksum(self):
        iban = 'LU28 0019 4006 4475 0001'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Malta (4a,5n,18c)   MTkk bbbb ssss sccc cccc cccc cccc ccc
    def test_MT_iban_valid_no_spaces(self):
        iban = 'MT84MALT011000012345MTLCAST001S'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 31, EntityRecognizer.MAX_SCORE)

    def test_MT_iban_valid_with_spaces(self):
        iban = 'MT84 MALT 0110 0001 2345 MTLC AST0 01S'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 38, EntityRecognizer.MAX_SCORE)
    
    def test_MT_iban_invalid_format_valid_checksum(self):
        iban = 'MT84 MALT A110 0001 2345 MTLC AST0 01S'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    def test_MT_iban_valid_checksum(self):
        iban = 'MT84 MALT 0110 0001 2345 MTLC AST0 01T'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Mauritania    (23n) MRkk bbbb bsss sscc cccc cccc cxx
    def test_MR_iban_valid_no_spaces(self):
        iban = 'MR1300020001010000123456753'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 27, EntityRecognizer.MAX_SCORE)

    def test_MR_iban_valid_with_spaces(self):
        iban = 'MR13 0002 0001 0100 0012 3456 753'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 33, EntityRecognizer.MAX_SCORE)
    
    def test_MR_iban_invalid_format_valid_checksum(self):
        iban = 'MR13 A002 0001 0100 0012 3456 753'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    def test_MR_iban_valid_checksum(self):
        iban = 'MR13 0002 0001 0100 0012 3456 754'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Mauritius (4a,19n,3a)   MUkk bbbb bbss cccc cccc cccc 000m mm
    def test_MU_iban_valid_no_spaces(self):
        iban = 'MU17BOMM0101101030300200000MUR'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 30, EntityRecognizer.MAX_SCORE)

    def test_MU_iban_valid_with_spaces(self):
        iban = 'MU17 BOMM 0101 1010 3030 0200 000M UR'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 37, EntityRecognizer.MAX_SCORE)
    
    def test_MU_iban_invalid_format_valid_checksum(self):
        iban = 'MU17 BOMM A101 1010 3030 0200 000M UR'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    def test_MU_iban_valid_checksum(self):
        iban = 'MU17 BOMM 0101 1010 3030 0200 000M US'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Moldova   (2c,18c)  MDkk bbcc cccc cccc cccc cccc
    def test_MD_iban_valid_no_spaces(self):
        iban = 'MD24AG000225100013104168'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 24, EntityRecognizer.MAX_SCORE)

    def test_MD_iban_valid_with_spaces(self):
        iban = 'MD24 AG00 0225 1000 1310 4168'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 29, EntityRecognizer.MAX_SCORE)
    
    def test_MD_iban_invalid_format_valid_checksum(self):
        iban = 'MD24 AG00 0225 1000 1310 4168 9'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    def test_MD_iban_valid_checksum(self):
        iban = 'MD24 AG00 0225 1000 1310 4169'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Monaco    (10n,11c,2n)  MCkk bbbb bsss sscc cccc cccc cxx
    def test_MC_iban_valid_no_spaces(self):
        iban = 'MC5811222000010123456789030'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 27, EntityRecognizer.MAX_SCORE)

    def test_MC_iban_valid_with_spaces(self):
        iban = 'MC58 1122 2000 0101 2345 6789 030'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 33, EntityRecognizer.MAX_SCORE)
    
    def test_MC_iban_invalid_format_valid_checksum(self):
        iban = 'MC58 A122 2000 0101 2345 6789 030'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    def test_MC_iban_valid_checksum(self):
        iban = 'MC58 1122 2000 0101 2345 6789 031'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Montenegro    (18n) MEkk bbbc cccc cccc cccc xx
    def test_ME_iban_valid_no_spaces(self):
        iban = 'ME25505000012345678951'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 22, EntityRecognizer.MAX_SCORE)

    def test_ME_iban_valid_with_spaces(self):
        iban = 'ME25 5050 0001 2345 6789 51'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 27, EntityRecognizer.MAX_SCORE)
    
    def test_ME_iban_invalid_format_valid_checksum(self):
        iban = 'ME25 A050 0001 2345 6789 51'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    def test_ME_iban_valid_checksum(self):
        iban = 'ME25 5050 0001 2345 6789 52'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Netherlands   (4a,10n)  NLkk bbbb cccc cccc cc
    def test_NL_iban_valid_no_spaces(self):
        iban = 'NL91ABNA0417164300'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 18, EntityRecognizer.MAX_SCORE)

    def test_NL_iban_valid_with_spaces(self):
        iban = 'NL91 ABNA 0417 1643 00'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 22, EntityRecognizer.MAX_SCORE)
    
    def test_NL_iban_invalid_format_valid_checksum(self):
        iban = 'NL91 1BNA 0417 1643 00'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    def test_NL_iban_valid_checksum(self):
        iban = 'NL91 ABNA 0417 1643 01'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # North Macedonia   (3n,10c,2n)   MKkk bbbc cccc cccc cxx
    def test_MK_iban_valid_no_spaces(self):
        iban = 'MK07250120000058984'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 19, EntityRecognizer.MAX_SCORE)

    def test_MK_iban_valid_with_spaces(self):
        iban = 'MK07 2501 2000 0058 984'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 23, EntityRecognizer.MAX_SCORE)
    
    def test_MK_iban_invalid_format_valid_checksum(self):
        iban = 'MK07 A501 2000 0058 984'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    def test_MK_iban_valid_checksum(self):
        iban = 'MK07 2501 2000 0058 985'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Norway    (11n) NOkk bbbb cccc ccx
    def test_NO_iban_valid_no_spaces(self):
        iban = 'NO9386011117947'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 15, EntityRecognizer.MAX_SCORE)

    def test_NO_iban_valid_with_spaces(self):
        iban = 'NO93 8601 1117 947'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 18, EntityRecognizer.MAX_SCORE)
    
    def test_NO_iban_invalid_format_valid_checksum(self):
        iban = 'NO93 A601 1117 947'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    def test_NO_iban_valid_checksum(self):
        iban = 'NO93 8601 1117 948'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Pakistan  (4c,16n)  PKkk bbbb cccc cccc cccc cccc
    def test_PK_iban_valid_no_spaces(self):
        iban = 'PK36SCBL0000001123456702'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 24, EntityRecognizer.MAX_SCORE)

    def test_PK_iban_valid_with_spaces(self):
        iban = 'PK36 SCBL 0000 0011 2345 6702'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 29, EntityRecognizer.MAX_SCORE)
    
    def test_PK_iban_invalid_format_valid_checksum(self):
        iban = 'PK36 SCBL A000 0011 2345 6702'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    def test_PK_iban_valid_checksum(self):
        iban = 'PK36 SCBL 0000 0011 2345 6703'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Palestinian territories   (4c,21n)  PSkk bbbb xxxx xxxx xccc cccc cccc c
    def test_PS_iban_valid_no_spaces(self):
        iban = 'PS92PALS000000000400123456702'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 29, EntityRecognizer.MAX_SCORE)

    def test_PS_iban_valid_with_spaces(self):
        iban = 'PS92 PALS 0000 0000 0400 1234 5670 2'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 36, EntityRecognizer.MAX_SCORE)
    
    def test_PS_iban_invalid_format_valid_checksum(self):
        iban = 'PS92 PALS A000 0000 0400 1234 5670 2'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    def test_PS_iban_valid_checksum(self):
        iban = 'PS92 PALS 0000 0000 0400 1234 5670 3'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Poland    (24n) PLkk bbbs sssx cccc cccc cccc cccc
    def test_PL_iban_valid_no_spaces(self):
        iban = 'PL61109010140000071219812874'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 28, EntityRecognizer.MAX_SCORE)

    def test_PL_iban_valid_with_spaces(self):
        iban = 'PL61 1090 1014 0000 0712 1981 2874'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 34, EntityRecognizer.MAX_SCORE)
    
    def test_PL_iban_invalid_format_valid_checksum(self):
        iban = 'PL61 A090 1014 0000 0712 1981 2874'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    def test_PL_iban_valid_checksum(self):
        iban = 'PL61 1090 1014 0000 0712 1981 2875'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Portugal  (21n) PTkk bbbb ssss cccc cccc cccx x
    def test_PT_iban_valid_no_spaces(self):
        iban = 'PT50000201231234567890154'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 25, EntityRecognizer.MAX_SCORE)

    def test_PT_iban_valid_with_spaces(self):
        iban = 'PT50 0002 0123 1234 5678 9015 4'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 31, EntityRecognizer.MAX_SCORE)
    
    def test_PT_iban_invalid_format_valid_checksum(self):
        iban = 'PT50 A002 0123 1234 5678 9015 4'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    def test_PT_iban_valid_checksum(self):
        iban = 'PT50 0002 0123 1234 5678 9015 5'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Qatar (4a,21c)  QAkk bbbb cccc cccc cccc cccc cccc c
    def test_QA_iban_valid_no_spaces(self):
        iban = 'QA58DOHB00001234567890ABCDEFG'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 29, EntityRecognizer.MAX_SCORE)

    def test_QA_iban_valid_with_spaces(self):
        iban = 'QA58 DOHB 0000 1234 5678 90AB CDEF G'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 36, EntityRecognizer.MAX_SCORE)
    
    def test_QA_iban_invalid_format_valid_checksum(self):
        iban = 'QA58 0OHB 0000 1234 5678 90AB CDEF G'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    def test_QA_iban_valid_checksum(self):
        iban = 'QA58 DOHB 0000 1234 5678 90AB CDEF H'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    #### Reunion

    # Romania   (4a,16c)  ROkk bbbb cccc cccc cccc cccc
    def test_RO_iban_valid_no_spaces(self):
        iban = 'RO49AAAA1B31007593840000'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 24, EntityRecognizer.MAX_SCORE)

    def test_RO_iban_valid_with_spaces(self):
        iban = 'RO49 AAAA 1B31 0075 9384 0000'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 29, EntityRecognizer.MAX_SCORE)
    
    def test_RO_iban_invalid_format_valid_checksum(self):
        iban = 'RO49 0AAA 1B31 0075 9384 0000'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    def test_RO_iban_valid_checksum(self):
        iban = 'RO49 AAAA 1B31 0075 9384 0001'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    ### Saint Barthelemy
    ### Saint Lucia
    ### Saint Martin
    ### Saint Pierrer 

    # San Marino    (1a,10n,12c)  SMkk xbbb bbss sssc cccc cccc ccc
    def test_SM_iban_valid_no_spaces(self):
        iban = 'SM86U0322509800000000270100'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 27, EntityRecognizer.MAX_SCORE)

    def test_SM_iban_valid_with_spaces(self):
        iban = 'SM86 U032 2509 8000 0000 0270 100'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 33, EntityRecognizer.MAX_SCORE)
    
    def test_SM_iban_invalid_format_valid_checksum(self):
        iban = 'SM86 0032 2509 8000 0000 0270 100'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    def test_SM_iban_valid_checksum(self):
        iban = 'SM86 U032 2509 8000 0000 0270 101'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    ### Sao Tome

    # Saudi Arabia  (2n,18c)  SAkk bbcc cccc cccc cccc cccc
    def test_SA_iban_valid_no_spaces(self):
        iban = 'SA0380000000608010167519'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 24, EntityRecognizer.MAX_SCORE)

    def test_SA_iban_valid_with_spaces(self):
        iban = 'SA03 8000 0000 6080 1016 7519'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 29, EntityRecognizer.MAX_SCORE)
    
    def test_SA_iban_invalid_format_valid_checksum(self):
        iban = 'SA03 A000 0000 6080 1016 7519'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    def test_SA_iban_valid_checksum(self):
        iban = 'SA03 8000 0000 6080 1016 7510'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Serbia    (18n) RSkk bbbc cccc cccc cccc xx
    def test_RS_iban_valid_no_spaces(self):
        iban = 'RS35260005601001611379'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 22, EntityRecognizer.MAX_SCORE)

    def test_RS_iban_valid_with_spaces(self):
        iban = 'RS35 2600 0560 1001 6113 79'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 27, EntityRecognizer.MAX_SCORE)
    
    def test_RS_iban_invalid_format_valid_checksum(self):
        iban = 'RS35 A600 0560 1001 6113 79'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    def test_RS_iban_valid_checksum(self):
        iban = 'RS35 2600 0560 1001 6113 70'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Slovakia  (20n) SKkk bbbb ssss sscc cccc cccc
    def test_RS_iban_valid_no_spaces(self):
        iban = 'SK3112000000198742637541'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 24, EntityRecognizer.MAX_SCORE)

    def test_RS_iban_valid_with_spaces(self):
        iban = 'SK31 1200 0000 1987 4263 7541'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 29, EntityRecognizer.MAX_SCORE)
    
    def test_RS_iban_invalid_format_valid_checksum(self):
        iban = 'SK31 A200 0000 1987 4263 7541'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    def test_RS_iban_valid_checksum(self):
        iban = 'SK31 1200 0000 1987 4263 7542'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Slovenia  (15n) SIkk bbss sccc cccc cxx
    def test_SI_iban_valid_no_spaces(self):
        iban = 'SI56263300012039086'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 19, EntityRecognizer.MAX_SCORE)

    def test_SI_iban_valid_with_spaces(self):
        iban = 'SI56 2633 0001 2039 086'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 23, EntityRecognizer.MAX_SCORE)
    
    def test_SI_iban_invalid_format_valid_checksum(self):
        iban = 'SI56 A633 0001 2039 086'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    def test_SI_iban_valid_checksum(self):
        iban = 'SI56 2633 0001 2039 087'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Spain (20n) ESkk bbbb ssss xxcc cccc cccc
    def test_ES_iban_valid_no_spaces(self):
        iban = 'ES9121000418450200051332'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 24, EntityRecognizer.MAX_SCORE)

    def test_ES_iban_valid_with_spaces(self):
        iban = 'ES91 2100 0418 4502 0005 1332'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 29, EntityRecognizer.MAX_SCORE)
    
    def test_ES_iban_invalid_format_valid_checksum(self):
        iban = 'ES91 A100 0418 4502 0005 1332'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    def test_ES_iban_valid_checksum(self):
        iban = 'ES91 2100 0418 4502 0005 1333'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Sweden    (20n) SEkk bbbc cccc cccc cccc cccc
    def test_SE_iban_valid_no_spaces(self):
        iban = 'SE4550000000058398257466'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 24, EntityRecognizer.MAX_SCORE)

    def test_SE_iban_valid_with_spaces(self):
        iban = 'SE45 5000 0000 0583 9825 7466'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 29, EntityRecognizer.MAX_SCORE)
    
    def test_SE_iban_invalid_format_valid_checksum(self):
        iban = 'SE45 A000 0000 0583 9825 7466'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    def test_SE_iban_valid_checksum(self):
        iban = 'SE45 5000 0000 0583 9825 7467'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Switzerland   (5n,12c)  CHkk bbbb bccc cccc cccc c
    def test_CH_iban_valid_no_spaces(self):
        iban = 'CH9300762011623852957'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 21, EntityRecognizer.MAX_SCORE)

    def test_CH_iban_valid_with_spaces(self):
        iban = 'CH93 0076 2011 6238 5295 7'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 26, EntityRecognizer.MAX_SCORE)
    
    def test_CH_iban_invalid_format_valid_checksum(self):
        iban = 'CH93 A076 2011 6238 5295 7'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    def test_CH_iban_valid_checksum(self):
        iban = 'CH93 0076 2011 6238 5295 8'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Tunisia   (20n) TNkk bbss sccc cccc cccc cccc
    def test_TN_iban_valid_no_spaces(self):
        iban = 'TN5910006035183598478831'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 24, EntityRecognizer.MAX_SCORE)

    def test_TN_iban_valid_with_spaces(self):
        iban = 'TN59 1000 6035 1835 9847 8831'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 29, EntityRecognizer.MAX_SCORE)
    
    def test_TN_iban_invalid_format_valid_checksum(self):
        iban = 'TN59 A000 6035 1835 9847 8831'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    def test_TN_iban_valid_checksum(self):
        iban = 'CH93 0076 2011 6238 5295 9'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Turkey    (5n,17c)  TRkk bbbb bxcc cccc cccc cccc cc
    def test_TR_iban_valid_no_spaces(self):
        iban = 'TR330006100519786457841326'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 26, EntityRecognizer.MAX_SCORE)

    def test_TR_iban_valid_with_spaces(self):
        iban = 'TR33 0006 1005 1978 6457 8413 26'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 32, EntityRecognizer.MAX_SCORE)
    
    def test_TR_iban_invalid_format_valid_checksum(self):
        iban = 'TR33 A006 1005 1978 6457 8413 26'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    def test_TR_iban_valid_checksum(self):
        iban = 'TR33 0006 1005 1978 6457 8413 27'
        results = iban_recognizer.analyze(iban, entities)
        
        assert len(results) == 0

    # United Arab Emirates  (3n,16n)  AEkk bbbc cccc cccc cccc ccc
    def test_AE_iban_valid_no_spaces(self):
        iban = 'AE070331234567890123456'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 23, EntityRecognizer.MAX_SCORE)

    def test_AE_iban_valid_with_spaces(self):
        iban = 'AE07 0331 2345 6789 0123 456'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 28, EntityRecognizer.MAX_SCORE)
    
    def test_AE_iban_invalid_format_valid_checksum(self):
        iban = 'AE07 A331 2345 6789 0123 456'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    def test_AE_iban_valid_checksum(self):
        iban = 'AE07 0331 2345 6789 0123 457'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # United Kingdom (4a,14n) GBkk bbbb ssss sscc cccc cc
    def test_GB_iban_valid_no_spaces(self):
        iban = 'GB29NWBK60161331926819'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 22, EntityRecognizer.MAX_SCORE)

    def test_GB_iban_valid_with_spaces(self):
        iban = 'GB29 NWBK 6016 1331 9268 19'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 27, EntityRecognizer.MAX_SCORE)
    
    def test_GB_iban_invalid_format_valid_checksum(self):
        iban = 'GB29 1WBK 6016 1331 9268 19'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    def test_GB_iban_valid_checksum(self):
        iban = 'GB29 NWBK 6016 1331 9268 10'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Vatican City  (3n,15n)  VAkk bbbc cccc cccc cccc cc
    def test_VA_iban_valid_no_spaces(self):
        iban = 'VA59001123000012345678'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 22, EntityRecognizer.MAX_SCORE)

    def test_VA_iban_valid_with_spaces(self):
        iban = 'VA59 0011 2300 0012 3456 78'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 27, EntityRecognizer.MAX_SCORE)
    
    def test_VA_iban_invalid_format_valid_checksum(self):
        iban = 'VA59 A011 2300 0012 3456 78'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    def test_VA_iban_valid_checksum(self):
        iban = 'VA59 0011 2300 0012 3456 79'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    # Virgin Islands, British   (4c,16n)  VGkk bbbb cccc cccc cccc cccc
    def test_VG_iban_valid_no_spaces(self):
        iban = 'VG96VPVG0000012345678901'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 24, EntityRecognizer.MAX_SCORE)

    def test_VG_iban_valid_with_spaces(self):
        iban = 'VG96 VPVG 0000 0123 4567 8901'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 29, EntityRecognizer.MAX_SCORE)
    
    def test_VG_iban_invalid_format_valid_checksum(self):
        iban = 'VG96 VPVG A000 0123 4567 8901'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    def test_VG_iban_valid_checksum(self):
        iban = 'VG96 VPVG 0000 0123 4567 8902'
        results = iban_recognizer.analyze(iban, entities)
        
        assert len(results) == 0

# Test Invalid IBANs    
    def test_iban_invalid_country_code_invalid_checksum(self):
        iban = 'AB150120690000003111141'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    def test_iban_invalid_country_code_valid_checksum(self):
        iban = 'AB150120690000003111141'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    def test_iban_too_short_valid_checksum(self):
        iban = 'IL15 0120 6900 0000'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    def test_iban_too_long_valid_checksum(self):
        iban = 'IL15 0120 6900 0000 3111 0120 6900 0000 3111 141'
        iban = update_iban_checksum(iban)
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0

    def test_invalid_IL_iban_with_exact_context_does_not_change_score(self):
        iban = 'IL150120690000003111141'
        context = 'my iban number is '
        results = iban_recognizer.analyze(context + iban, entities)

        assert len(results) == 0

    def test_AL_iban_invalid_country_code_but_checksum_is_correct(self):
        iban = 'AM47212110090000000235698740'
        results = iban_recognizer.analyze(iban, entities)

        assert len(results) == 0
