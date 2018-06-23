import sys
import os

import logging
import pathlib
import pandas as pd


def scan_multiple_files():
    dirpath = "/Users/torosent/prodigy/prodigy/enron/emails"

    i = 0
    total = 10
    j = 0
    x = []
    y = []
    x1 = []
    for path, subdirs, files in os.walk(dirpath):
        if i == total:
            break
        for name in files:
            if name.lower().endswith('.txt') == False:
                continue
            j = j + 1
            if i == total:
                break

            file = pathlib.PurePath(path, name)
            text_file = open(file, 'r')
            text = text_file.read()
            text_file.close()

            def clear(): return os.system('clear')
            clear()
            print(text)
            input_text = input(
                f"Yes (Y) / No (N) - T{j} TT{i} ")
            if input_text.upper() == "Y":
                i = i + 1
                y.append("True")
            else:
                y.append("False")
            x.append(text)
            x1.append(file)
    df = pd.DataFrame({'text': x, 'result': y, 'path': x1})
    writer = pd.ExcelWriter('output.xlsx')
    df.to_excel(writer, 'Sheet1')
    writer.save()


scan_multiple_files()
