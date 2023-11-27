"""Helper data classes, mostly simple wrappers  to ensure consistent user interface."""

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Union

import pandas as pd


class ReaderBase(ABC):
    """
    Base class for data readers.

    This class should not be instantiated directly, instead init a subclass.
    """

    @abstractmethod
    def read(self, path: Union[str, Path], **kwargs) -> Any:
        """
        Extract data from file located at path.

        :param path: String defining the location of the file to read.
        :return: The data read from the file.
        """
        pass


class CsvReader(ReaderBase):
    """
    Reader for reading csv files.

    Usage::

        reader = CsvReader()
        data = reader.read(path="filepath.csv")

    """

    def read(self, path: Union[str, Path], **kwargs) -> pd.DataFrame:
        """
        Read csv file to pandas dataframe.

        :param path: String defining the location of the csv file to read.
        :return: Pandas DataFrame with the data read from the csv file.
        """
        return pd.read_csv(path, **kwargs)


class JsonReader(ReaderBase):
    """
    Reader for reading json files.

    Usage::

        reader = JsonReader()
        data = reader.read(path="filepath.json")

    """

    def read(self, path: Union[str, Path], **kwargs) -> Dict[str, Any]:
        """
        Read json file to dict.

        :param path: String defining the location of the json file to read.
        :return: dictionary with the data read from the json file.
        """
        with open(path) as f:
            data = json.load(f, **kwargs)
        return data
