# from analyzer import matcher
# import logging
# import os
# import pathlib
# types = ["PHONE_NUMBER", "CREDIT_CARD", "EMAIL"]


# def test_multiple_files():
#     match = matcher.Matcher()
#     dirpath = ""
#     output_file = open(enron.json”, ”w”)
#     for path, subdirs, files in os.walk(dirpath):
#         for name in files:
#             if name == ".DS_Store":
#                 continue

#             file = pathlib.PurePath(path, name)
#             size = os.stat(file).st_size
#             logging.info(f"{file} size: {size}")
#             text_file = open(file, 'r')
#             text = text_file.read()
#             results = match.analyze_text(text, types)
#             text_file.close()
