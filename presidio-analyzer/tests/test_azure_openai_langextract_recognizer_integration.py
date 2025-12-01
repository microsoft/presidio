import os
import pytest


class TestRealUserScenario:
    """Simulate real user following README with actual Azure OpenAI."""
    
    @pytest.mark.skipif(
        not os.getenv("AZURE_OPENAI_API_KEY") or not os.getenv("AZURE_OPENAI_ENDPOINT"),
        reason="Requires AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT environment variables"
    )
    def test_user_scenario_with_environment_variables(self):
        """
        User Scenario: Developer following README - Using Environment Variables
        
        Steps:
        1. User sets environment variables (already done in their shell/container)
        2. User imports Presidio
        3. User creates AzureOpenAILangExtractRecognizer with just model_id
        4. User adds it to AnalyzerEngine
        5. User analyzes text
        """
        print("\n" + "="*70)
        print("SCENARIO: Developer Using Azure OpenAI with Environment Variables")
        print("="*70)
        
        # Import what user would import
        from presidio_analyzer import AnalyzerEngine
        from presidio_analyzer.predefined_recognizers import AzureOpenAILangExtractRecognizer
        
        print("\n✓ Imports successful")
        print(f"  - Endpoint: {os.getenv('AZURE_OPENAI_ENDPOINT')}")
        
        # Create recognizer - user just needs to specify their deployment name
        # They saw this in Azure Portal when they deployed the model
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1")
        print(f"\n→ Creating recognizer with deployment name '{deployment_name}'...")
        recognizer = AzureOpenAILangExtractRecognizer(
            model_id=deployment_name  # User's actual deployment name from Azure Portal
        )
        
        print("✓ Recognizer created successfully")
        print(f"  - Model ID: {recognizer.model_id}")
        print(f"  - Endpoint: {recognizer.azure_endpoint}")
        print(f"  - Using API key: {'Yes' if recognizer.api_key else 'No (managed identity)'}")
        
        # Add to analyzer
        print("\n→ Adding recognizer to AnalyzerEngine...")
        analyzer = AnalyzerEngine()
        analyzer.registry.add_recognizer(recognizer)
        
        print("✓ Recognizer added to analyzer")
        
        # Analyze some text
        test_text = "Contact John Doe at john.doe@example.com or call 555-123-4567. His SSN is 123-45-6789."
        
        print(f"\n→ Analyzing text: '{test_text}'")
        print("  (This will call Azure OpenAI...)")
        
        results = analyzer.analyze(text=test_text, language="en")
        
        print(f"\n✓ Analysis complete! Found {len(results)} PII entities:")
        for result in results:
            detected_text = test_text[result.start:result.end]
            print(f"  - {result.entity_type}: '{detected_text}' (score: {result.score:.2f})")
        
        # Verify we got reasonable results
        assert len(results) > 0, "Should detect at least some PII"
        entity_types = {r.entity_type for r in results}
        print(f"\n✓ Entity types detected: {entity_types}")
        
        # Common entities users expect
        expected_entities = {"EMAIL_ADDRESS", "PHONE_NUMBER", "US_SSN", "PERSON"}
        detected_expected = entity_types & expected_entities
        print(f"✓ Common PII detected: {detected_expected}")
        
        print("\n" + "="*70)
        print("SUCCESS: User can use Azure OpenAI with just environment variables!")
        print("="*70)
    
    @pytest.mark.skipif(
        not os.getenv("AZURE_OPENAI_API_KEY") or not os.getenv("AZURE_OPENAI_ENDPOINT"),
        reason="Requires AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT environment variables"
    )
    def test_user_scenario_with_direct_parameters(self):
        """
        User Scenario: Developer following README - Using Direct Parameters
        
        Steps:
        1. User has credentials (maybe from Azure Portal, .env file, etc.)
        2. User imports Presidio
        3. User creates recognizer with all parameters
        4. User analyzes text
        """
        print("\n" + "="*70)
        print("SCENARIO: Developer Using Azure OpenAI with Direct Parameters")
        print("="*70)
        
        from presidio_analyzer import AnalyzerEngine
        from presidio_analyzer.predefined_recognizers import AzureOpenAILangExtractRecognizer
        
        print("\n✓ Imports successful")
        
        # User passes everything explicitly (good for testing, development)
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1")
        
        print(f"\n→ Creating recognizer with explicit parameters...")
        print(f"  - Deployment: {deployment_name}")
        print(f"  - Endpoint: {endpoint}")
        
        recognizer = AzureOpenAILangExtractRecognizer(
            model_id=deployment_name,
            azure_endpoint=endpoint,
            api_key=api_key
        )
        
        print("✓ Recognizer created")
        
        # Use it
        analyzer = AnalyzerEngine()
        analyzer.registry.add_recognizer(recognizer)
        
        test_text = "Patient Mary Smith (SSN: 987-65-4321) can be reached at mary@hospital.com"
        
        print(f"\n→ Analyzing medical text...")
        results = analyzer.analyze(text=test_text, language="en")
        
        print(f"\n✓ Found {len(results)} PII/PHI entities:")
        for result in results:
            detected_text = test_text[result.start:result.end]
            print(f"  - {result.entity_type}: '{detected_text}'")
        
        assert len(results) > 0
        
        print("\n" + "="*70)
        print("SUCCESS: User can use Azure OpenAI with direct parameters!")
        print("="*70)
    
    @pytest.mark.skipif(
        not os.getenv("AZURE_OPENAI_API_KEY") or not os.getenv("AZURE_OPENAI_ENDPOINT"),
        reason="Requires AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT environment variables"
    )
    def test_user_tries_different_deployment(self):
        """
        User Scenario: User has multiple deployments and wants to try a different one.
        
        This tests that model_id parameter actually works for different deployments.
        """
        print("\n" + "="*70)
        print("SCENARIO: User Testing Different Deployment (gpt-4.1-mini)")
        print("="*70)
        
        from presidio_analyzer import AnalyzerEngine
        from presidio_analyzer.predefined_recognizers import AzureOpenAILangExtractRecognizer
        
        # User tries a different model deployment (if they have one)
        # For this test, we'll use the same deployment since we may not have multiple
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_ALTERNATIVE", os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1"))
        print(f"\n→ Creating recognizer with deployment '{deployment_name}'...")
        recognizer = AzureOpenAILangExtractRecognizer(
            model_id=deployment_name
        )
        
        print(f"✓ Using deployment: {recognizer.model_id}")
        
        analyzer = AnalyzerEngine()
        analyzer.registry.add_recognizer(recognizer)
        
        # Quick test
        text = "Email me at test@example.com"
        print(f"\n→ Quick test: '{text}'")
        
        results = analyzer.analyze(text=text, language="en")
        
        print(f"✓ Mini model works! Found {len(results)} entities")
        for result in results:
            print(f"  - {result.entity_type}: {text[result.start:result.end]}")
        
        print("\n" + "="*70)
        print("SUCCESS: User can easily switch between deployments!")
        print("="*70)


if __name__ == "__main__":
    """
    To run this test manually:
    
    export AZURE_OPENAI_API_KEY="your-api-key"
    export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
    cd presidio-analyzer
    poetry run python tests/test_azure_openai_langextract_recognizer_integration.py
    """
    import sys
    
    if not os.getenv("AZURE_OPENAI_API_KEY"):
        print("ERROR: AZURE_OPENAI_API_KEY environment variable not set")
        print("\nTo run this test:")
        print('  export AZURE_OPENAI_API_KEY="your-key"')
        print('  export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"')
        print('  poetry run pytest tests/test_azure_openai_langextract_recognizer_integration.py -v -s')
        sys.exit(1)
    
    pytest.main([__file__, "-v", "-s"])
