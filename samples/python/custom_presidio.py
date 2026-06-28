from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern

if __name__ == "__main__":

    analyzer = AnalyzerEngine()

    text1 = "Professor Plum, in the Dining Room, with the candlestick"

    titles_list = [
        "Sir",
        "Ma'am",
        "Madam",
        "Mr.",
        "Mrs.",
        "Ms.",
        "Miss",
        "Dr.",
        "Professor",
    ]
    titles_recognizer = PatternRecognizer(
        supported_entity="TITLE", deny_list=titles_list
    )
    analyzer.registry.add_recognizer(titles_recognizer)

    result = analyzer.analyze(text=text1, language="en")
    print(f"\nDeny List result:\n {result}")

    text2 = "I live in 510 Broad st."

    numbers_pattern = Pattern(name="numbers_pattern", regex=r"\d+", score=0.5)
    number_recognizer = PatternRecognizer(
        supported_entity="NUMBER", patterns=[numbers_pattern]
    )

    result = number_recognizer.analyze(text=text2, entities=["NUMBER"])
    print(f"\nRegex result:\n {result}")
