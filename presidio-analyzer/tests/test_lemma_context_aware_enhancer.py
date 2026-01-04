from presidio_analyzer import LemmaContextAwareEnhancer


def test_when_index_finding_then_succeed():
    # This test uses a simulated recognize result for the following
    # text: "my phone number is:(425) 882-9090"
    match = "(425) 882-9090"
    # the start index of the match
    start = 19
    tokens = ["my", "phone", "number", "is:(425", ")", "882", "-", "9090"]
    tokens_indices = [0, 3, 9, 16, 23, 25, 28, 29]
    index = LemmaContextAwareEnhancer._find_index_of_match_token(
        match, start, tokens, tokens_indices
    )
    assert index == 3


def test_when_context_word_substring_then_no_false_match():
    """
    Test that substring matching does not cause false positives.
    
    This test verifies the fix for issue #1061 where 'lic' was matching
    'duplicate' as a substring. With whole-word matching, 'lic' should
    only match 'lic' exactly, not substrings like 'duplicate'.
    """
    context_list = ["duplicate", "license", "driver"]
    recognizer_context_list = ["lic"]
    
    result = LemmaContextAwareEnhancer._find_supportive_word_in_context(
        context_list, recognizer_context_list
    )
    
    # 'lic' should NOT match 'duplicate' (substring match - should be False)
    # 'lic' should NOT match 'license' (not exact match - should be False)
    # 'lic' should NOT match 'driver' (not exact match - should be False)
    assert result == ""


def test_when_context_word_exact_match_then_succeed():
    """
    Test that exact whole-word matches work correctly.
    
    'lic' should match 'lic' exactly (case-insensitive).
    """
    context_list = ["lic", "license", "driver"]
    recognizer_context_list = ["lic"]
    
    result = LemmaContextAwareEnhancer._find_supportive_word_in_context(
        context_list, recognizer_context_list
    )
    
    # 'lic' should match 'lic' exactly
    assert result == "lic"


def test_when_context_word_case_insensitive_then_succeed():
    """
    Test that matching is case-insensitive.
    
    'LIC' should match 'lic' and vice versa.
    """
    context_list = ["LIC", "license", "driver"]
    recognizer_context_list = ["lic"]
    
    result = LemmaContextAwareEnhancer._find_supportive_word_in_context(
        context_list, recognizer_context_list
    )
    
    # 'lic' should match 'LIC' (case-insensitive)
    assert result == "lic"
    
    # Test reverse case
    context_list = ["lic", "license", "driver"]
    recognizer_context_list = ["LIC"]
    
    result = LemmaContextAwareEnhancer._find_supportive_word_in_context(
        context_list, recognizer_context_list
    )
    
    # 'LIC' should match 'lic' (case-insensitive)
    assert result == "LIC"


def test_when_context_word_multiple_matches_then_first_match_returned():
    """
    Test that when multiple context words match, the first one is returned.
    """
    context_list = ["driver", "license", "permit"]
    recognizer_context_list = ["license", "driver", "permit"]
    
    result = LemmaContextAwareEnhancer._find_supportive_word_in_context(
        context_list, recognizer_context_list
    )
    
    # Should return the first match from recognizer_context_list
    assert result == "license"


def test_when_context_word_no_match_then_empty_string():
    """
    Test that when no context words match, empty string is returned.
    """
    context_list = ["random", "words", "here"]
    recognizer_context_list = ["lic", "driver", "license"]
    
    result = LemmaContextAwareEnhancer._find_supportive_word_in_context(
        context_list, recognizer_context_list
    )
    
    assert result == ""


def test_when_duplicate_word_in_text_then_lic_context_not_matched(
    spacy_nlp_engine,
):
    """
    Integration test for issue #1061: 'lic' should not match 'duplicate'.
    
    This test verifies that when the word 'duplicate' appears in text,
    the context word 'lic' (from US_DRIVER_LICENSE recognizer) should
    NOT cause false context enhancement.
    """
    from presidio_analyzer import PatternRecognizer, Pattern
    from presidio_analyzer.context_aware_enhancers import LemmaContextAwareEnhancer
    
    # Create a recognizer with 'lic' as context word (similar to US_DRIVER_LICENSE)
    test_recognizer = PatternRecognizer(
        supported_entity="TEST_LICENSE",
        name="test_license_recognizer",
        context=["lic"],  # This is the problematic context word
        patterns=[Pattern("test_pattern", r"\b[A-Z0-9]{8}\b", 0.3)],
    )
    
    # Test case 1: Text with 'duplicate' but no actual license context words
    # The word 'duplicate' contains 'lic' as a substring, but should NOT match
    text = "This is a duplicate document with code ABC12345"
    nlp_artifacts = spacy_nlp_engine.process_text(text, "en")
    
    recognizer_results = test_recognizer.analyze(text, nlp_artifacts)
    assert len(recognizer_results) > 0
    
    original_score = recognizer_results[0].score
    
    enhancer = LemmaContextAwareEnhancer()
    enhanced_results = enhancer.enhance_using_context(
        text, recognizer_results, nlp_artifacts, [test_recognizer]
    )
    
    # With whole-word matching, 'lic' should NOT match 'duplicate'
    # So the score should NOT be enhanced and supportive_context_word should be empty
    assert enhanced_results[0].score == original_score
    assert (
        enhanced_results[0].analysis_explanation.supportive_context_word == ""
    )
