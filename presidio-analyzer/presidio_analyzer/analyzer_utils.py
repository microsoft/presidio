from typing import List, Tuple
import csv
import os


class PresidioAnalyzerUtils:
    """
    Utility functions for Presidio Analyzer.

    The class provides a bundle of utility functions that help centralizing the
    logic for re-usability and maintainability
    """

    __country_master_file_path__ = "presidio_analyzer/country_master.csv"
    __country_master__ = []

    def __init__(self):
        self.__load_country_master__()

    @staticmethod
    def is_palindrome(text: str, case_insensitive: bool = False):
        """
        Validate if input text is a true palindrome.

        :param text: input text string to check for palindrome
        :param case_insensitive: optional flag to check palindrome with no case
        :return: True / False
        """
        palindrome_text = text
        if case_insensitive:
            palindrome_text = palindrome_text.replace(" ", "").lower()
        return palindrome_text == palindrome_text[::-1]

    @staticmethod
    def sanitize_value(text: str, replacement_pairs: List[Tuple[str, str]]) -> str:
        """
        Cleanse the input string of the replacement pairs specified as argument.

        :param text: input string
        :param replacement_pairs: pairs of what has to be replaced with which value
        :return: cleansed string
        """
        for search_string, replacement_string in replacement_pairs:
            text = text.replace(search_string, replacement_string)
        return text

    @staticmethod
    def get_luhn_mod_n(input_str: str, alphabet="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        """
        Check if the given input number has a valid last checksum as per LUHN algorithm.

        https://en.wikipedia.org/wiki/Luhn_mod_N_algorithm
        :param alphabet: input alpha-numeric list of characters to determine mod 'N'
        :param input_str: the alpha numeric string to be checked for LUHN algorithm
        :return: True/False
        """
        if len(alphabet) == 0:
            return False

        charset = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        n = len(charset)
        luhn_input = tuple(alphabet.index(i) for i in reversed(str(input_str)))
        return (
            sum(luhn_input[::2]) + sum(sum(divmod(i * 2, n)) for i in luhn_input[1::2])
        ) % n == 0

    @staticmethod
    def is_verhoeff_number(input_number: int):
        """
        Check if the input number is a true verhoeff number.

        :param input_number:
        :return: Bool
        """
        __d__ = [
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
            [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
            [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
            [4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
            [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
            [6, 5, 9, 8, 7, 1, 0, 4, 3, 2],
            [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
            [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
            [9, 8, 7, 6, 5, 4, 3, 2, 1, 0],
        ]
        __p__ = [
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
            [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
            [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
            [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
            [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
            [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
            [7, 0, 4, 6, 9, 1, 3, 2, 5, 8],
        ]
        __inv__ = [0, 4, 3, 2, 1, 5, 6, 7, 8, 9]

        c = 0
        inverted_number = list(map(int, reversed(str(input_number))))
        for i in range(len(inverted_number)):
            c = __d__[c][__p__[i % 8][inverted_number[i]]]
        return __inv__[c] == 0

    def __load_country_master__(self):
        """
        Load various standards as defined in  Country specific metadata.

        :return: None
        """
        if os.path.isfile(self.__country_master_file_path__) is not True:
            raise FileNotFoundError()
        else:
            with open(
                file=self.__country_master_file_path__,
                mode="r",
                newline="",
                encoding="utf-8",
            ) as csvfile:
                if csv.Sniffer().has_header(csvfile.readline()) is not True:
                    raise Exception(
                        "Header missing in file: {}".format(
                            self.__country_master_file_path__
                        )
                    )
                csvfile.seek(0)  # read the header as well, hence start from beginning
                country_info = csv.DictReader(csvfile, fieldnames=None)
                self.__country_master__ = list(country_info)

        if len(self.__country_master__) <= 1:
            raise Exception(
                "Blank file: {} detected.".format(self.__country_master_file_path__)
            )

    def __get_country_master_full_data__(self, iso_code: str = ""):
        """
        Fetch all country information for a specific column (index).

        :param iso_code:
        :return:
        """
        supported_codes = [
            "ISO3166-1-Alpha-2",
            "ISO3166-1-Alpha-3",
            "ISO3166-1-Numeric",
            "ISO4217-Alpha-3",
            "ISO4217-Numeric",
        ]
        if iso_code.strip() not in supported_codes:
            return None
        else:
            # return full country list for given code
            country_information = [
                country[iso_code] for country in self.__country_master__
            ]
            country_information = list(filter(None, country_information))
            return country_information

    def get_country_codes(self, iso_code: str):
        """
        Fetch all defined country codes per required ISO format.

        :param iso_code: currently supporting : ISO3166-1-Alpha-2,
        ISO3166-1-Alpha-3, ISO3166-1-Numeric
        :return: List of country codes in provided ISO format.
        """
        supported_codes = [
            "ISO3166-1-Alpha-2",
            "ISO3166-1-Alpha-3",
            "ISO3166-1-Numeric",
        ]
        if iso_code.strip() not in supported_codes:
            print("Code Invalid: ")
            return None
        else:
            # return full country list for given code
            return self.__get_country_master_full_data__(iso_code=iso_code)

    def get_currency_codes(self, iso_code: str = ""):
        """
        Retrieve all defined currency codes across countries.

         :param iso_code: currently supporting : ISO4217-Alpha-3, ISO4217-Numeric
         :return: List of currency codes in provided ISO format.
        """
        supported_codes = ["ISO4217-Alpha-3", "ISO4217-Numeric"]
        if iso_code.strip() not in supported_codes:
            return None
        else:
            # return full country list for given code
            return self.__get_country_master_full_data__(iso_code=iso_code)

    def get_full_country_information(self, lookup_key: str, lookup_index: str):
        """
        Fetch additional information through lookup_index in index of lookup_key.

        :param lookup_key: Item to be searched
        :param lookup_index: A valid index_name out of available values
        English_short_name_using_title_case, English_full_name,
        FIFA_country_code, International_olympic_committee_country_code,
        ISO3166-1-Alpha-2,ISO3166-1-Alpha-3, ISO3166-1-Numeric,
        International_licence_plate_country_code, Country_code_top_level_domain,
        Currency_Name, ISO4217-Alpha-3, ISO4217-Numeric, Capital_City, Dialing_Code
        :return: Dictionary object with additional information enriched from
        master lookup

        """
        allowed_indices = [
            "English_short_name_using_title_case",
            "English_full_name",
            "FIFA_country_code",
            "International_olympic_committee_country_code",
            "ISO3166-1-Alpha-2",
            "ISO3166-1-Alpha-3",
            "ISO3166-1-Numeric",
            "International_licence_plate_country_code",
            "Country_code_top_level_domain",
            "Currency_Name",
            "ISO4217-Alpha-3",
            "ISO4217-Numeric",
            "Capital_City",
            "Dialing_Code",
        ]
        if (
            lookup_index is None
            or len(lookup_index.strip()) == 0
            or lookup_index not in allowed_indices
        ):
            print("Lookup Index problem")
            return None
        elif lookup_key is None or len(lookup_key.strip()) == 0:
            print("Lookup Key issue")
            return None
        else:
            return list(
                filter(
                    lambda country: country[lookup_index] == lookup_key,
                    self.__country_master__,
                )
            )
