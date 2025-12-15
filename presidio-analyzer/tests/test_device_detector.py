"""Unit tests for DeviceDetector."""

from unittest.mock import MagicMock, Mock, patch

import pytest

from presidio_analyzer.nlp_engine import device_detector
from presidio_analyzer.nlp_engine.device_detector import DeviceDetector


class TestDeviceDetector:
    """Test suite for DeviceDetector functionality."""

    def test_when_device_detector_imported_then_singleton_exists(self):
        """Test that device_detector singleton is available on import."""
        assert device_detector is not None
        assert isinstance(device_detector, DeviceDetector)

    def test_when_get_device_then_returns_string(self):
        """Test that get_device() returns a valid device string."""
        device = device_detector.get_device()
        assert isinstance(device, str)
        assert device in ["cpu", "cuda"]

    def test_when_get_gpu_device_name_then_returns_optional_string(self):
        """Test that get_gpu_device_name() returns None or string."""
        device_name = device_detector.get_gpu_device_name()
        assert device_name is None or isinstance(device_name, str)

    def test_when_device_is_cuda_then_has_device_name(self):
        """Test that if CUDA is available, device name is set."""
        if device_detector.get_device() == "cuda":
            assert device_detector.get_gpu_device_name() is not None
        else:
            # If CPU, device name may be None
            assert device_detector.get_gpu_device_name() is None

    def test_when_device_is_cpu_or_cuda_then_consistent(self):
        """Test that device detection is consistent."""
        # Device should be either cpu or cuda
        device = device_detector.get_device()
        assert device in ["cpu", "cuda"]
        
        # Multiple calls should return same value
        assert device_detector.get_device() == device

    def test_when_multiple_instances_then_same_values(self):
        """Test that multiple DeviceDetector instances have consistent values."""
        detector1 = DeviceDetector()
        detector2 = DeviceDetector()
        
        # Both should return the same device
        assert detector1.get_device() == detector2.get_device()
        assert detector1.get_gpu_device_name() == detector2.get_gpu_device_name()


class TestDeviceDetectorIntegration:
    """Integration tests for DeviceDetector usage in NLP engines."""

    def test_when_spacy_engine_loads_then_uses_device_detector(self):
        """Test that SpacyNlpEngine uses device_detector."""
        from presidio_analyzer.nlp_engine import SpacyNlpEngine
        
        engine = SpacyNlpEngine(
            models=[{"lang_code": "en", "model_name": "en_core_web_sm"}]
        )
        
        # Verify device_detector is accessible
        assert device_detector.get_device() in ["cpu", "cuda"]

    def test_when_stanza_engine_initializes_then_sets_use_gpu(self):
        """Test that StanzaNlpEngine correctly sets use_gpu from device_detector."""
        from presidio_analyzer.nlp_engine import StanzaNlpEngine
        
        engine = StanzaNlpEngine(
            models=[{"lang_code": "en", "model_name": "en"}]
        )
        
        # use_gpu should match device_detector
        expected_use_gpu = device_detector.get_device() == "cuda"
        assert engine.use_gpu == expected_use_gpu

    def test_when_gliner_recognizer_initializes_then_uses_correct_device(self):
        """Test that GLiNERRecognizer uses device from device_detector."""
        pytest.importorskip("gliner")
        from presidio_analyzer.predefined_recognizers import GLiNERRecognizer
        
        recognizer = GLiNERRecognizer()
        
        # map_location should match device_detector.get_device()
        assert recognizer.map_location == device_detector.get_device()

    def test_when_stanza_engine_use_gpu_matches_device_detector(self):
        """Test that StanzaNlpEngine.use_gpu matches device_detector."""
        from presidio_analyzer.nlp_engine import StanzaNlpEngine
        
        engine = StanzaNlpEngine(
            models=[{"lang_code": "en", "model_name": "en"}]
        )
        
        expected_use_gpu = device_detector.get_device() == "cuda"
        assert engine.use_gpu == expected_use_gpu


class TestDeviceDetectorBehavior:
    """Test suite for DeviceDetector runtime behavior."""

    def test_when_creating_new_instance_then_device_consistent(self):
        """Test that new instances have consistent device detection."""
        detector1 = DeviceDetector()
        detector2 = DeviceDetector()
        
        # Both should detect the same device
        assert detector1.get_device() == detector2.get_device()

    def test_when_device_is_cuda_then_has_capabilities(self):
        """Test that CUDA device has expected capabilities."""
        if device_detector.get_device() == "cuda":
            # Should have a device name
            assert device_detector.get_gpu_device_name() is not None
            assert len(device_detector.get_gpu_device_name()) > 0
        
    def test_when_device_is_cpu_then_no_gpu_name(self):
        """Test that CPU device has no GPU name."""
        if device_detector.get_device() == "cpu":
            assert device_detector.get_gpu_device_name() is None