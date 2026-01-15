"""Unit tests for DeviceDetector."""

import os
from unittest.mock import MagicMock, patch

import pytest

from presidio_analyzer.nlp_engine.device_detector import (
    DeviceDetector,
    PRESIDIO_DEVICE_ENV_VAR,
    device_detector,
)


class TestDeviceDetectorEnvironmentVariable:
    """Test suite for PRESIDIO_DEVICE environment variable handling."""

    def test_when_env_var_set_to_cpu_then_uses_cpu(self):
        """Test that CPU is used when PRESIDIO_DEVICE=cpu."""
        with patch.dict(os.environ, {PRESIDIO_DEVICE_ENV_VAR: "cpu"}):
            detector = DeviceDetector()
            assert detector.get_device() == "cpu"

    def test_when_env_var_set_to_cuda_then_uses_cuda(self):
        """Test that CUDA is used when PRESIDIO_DEVICE=cuda."""
        with patch.dict(os.environ, {PRESIDIO_DEVICE_ENV_VAR: "cuda"}):
            detector = DeviceDetector()
            assert detector.get_device() == "cuda"

    def test_when_env_var_set_to_specific_gpu_then_uses_it(self):
        """Test that specific GPU device strings are passed through."""
        with patch.dict(os.environ, {PRESIDIO_DEVICE_ENV_VAR: "cuda:0"}):
            detector = DeviceDetector()
            assert detector.get_device() == "cuda:0"

        with patch.dict(os.environ, {PRESIDIO_DEVICE_ENV_VAR: "cuda:1"}):
            detector = DeviceDetector()
            assert detector.get_device() == "cuda:1"

    def test_when_env_var_has_whitespace_then_trimmed(self):
        """Test that whitespace in env var value is trimmed."""
        with patch.dict(os.environ, {PRESIDIO_DEVICE_ENV_VAR: "  cpu  "}):
            detector = DeviceDetector()
            assert detector.get_device() == "cpu"

        with patch.dict(os.environ, {PRESIDIO_DEVICE_ENV_VAR: "  cuda:0  "}):
            detector = DeviceDetector()
            assert detector.get_device() == "cuda:0"

    def test_when_env_var_empty_then_auto_detects(self):
        """Test that empty env var triggers auto-detection."""
        with patch.dict(os.environ, {PRESIDIO_DEVICE_ENV_VAR: ""}):
            detector = DeviceDetector()
            assert detector.get_device() in ["cpu", "cuda"]

    def test_when_env_var_not_set_then_auto_detects(self):
        """Test that missing env var triggers auto-detection."""
        env_without_presidio_device = {
            k: v for k, v in os.environ.items() if k != PRESIDIO_DEVICE_ENV_VAR
        }
        with patch.dict(os.environ, env_without_presidio_device, clear=True):
            detector = DeviceDetector()
            assert detector.get_device() in ["cpu", "cuda"]

    def test_when_env_var_set_skips_auto_detection(self):
        """Test that setting env var skips auto-detection entirely."""
        with patch.dict(os.environ, {PRESIDIO_DEVICE_ENV_VAR: "cpu"}):
            with patch.object(DeviceDetector, "_detect") as mock_detect:
                detector = DeviceDetector()
                mock_detect.assert_not_called()
                assert detector.get_device() == "cpu"


class TestDeviceDetectorErrorPaths:
    """Test suite for DeviceDetector error handling."""

    def test_when_torch_import_fails_then_cpu_device(self):
        """Test that CPU is used when PyTorch import fails."""
        with patch("builtins.__import__", side_effect=ImportError("No module named 'torch'")):
            detector = DeviceDetector()
            
            assert detector.get_device() == "cpu"

    def test_when_cuda_not_available_then_cpu_device(self):
        """Test that CPU is used when CUDA is not available."""
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = False
        
        def mock_import(name, *args):
            if name == "torch":
                return mock_torch
            return __builtins__.__import__(name, *args)
        
        with patch("builtins.__import__", side_effect=mock_import):
            detector = DeviceDetector()
            
            assert detector.get_device() == "cpu"

    def test_when_cuda_initialization_fails_then_fallback_to_cpu(self):
        """Test that CPU fallback occurs when CUDA initialization fails."""
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = True
        mock_torch.tensor.side_effect = RuntimeError("CUDA initialization error")
        
        def mock_import(name, *args):
            if name == "torch":
                return mock_torch
            return __builtins__.__import__(name, *args)
        
        with patch("builtins.__import__", side_effect=mock_import):
            detector = DeviceDetector()
            
            assert detector.get_device() == "cpu"

    def test_when_cuda_get_device_name_fails_then_fallback_to_cpu(self):
        """Test fallback when get_device_name fails."""
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = True
        mock_torch.tensor.return_value = MagicMock(__str__=lambda x: "tensor")
        mock_torch.cuda.get_device_name.side_effect = RuntimeError("Device name error")
        
        def mock_import(name, *args):
            if name == "torch":
                return mock_torch
            return __builtins__.__import__(name, *args)
        
        with patch("builtins.__import__", side_effect=mock_import):
            detector = DeviceDetector()
            
            assert detector.get_device() == "cpu"

    def test_when_cuda_available_then_cuda_device(self):
        """Test successful CUDA detection."""
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = True
        mock_torch.tensor.return_value = MagicMock(__str__=lambda x: "tensor")
        mock_torch.cuda.get_device_name.return_value = "Test GPU"
        mock_torch.cuda.get_device_capability.return_value = (8, 0)
        
        def mock_import(name, *args):
            if name == "torch":
                return mock_torch
            return __builtins__.__import__(name, *args)
        
        with patch("builtins.__import__", side_effect=mock_import):
            detector = DeviceDetector()
            
            assert detector.get_device() == "cuda"

    def test_when_cuda_available_then_uses_cuda_not_cpu(self):
        """Test that CUDA is used when available (MPS is not supported)."""
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = True
        mock_torch.tensor.return_value = MagicMock(__str__=lambda x: "tensor")
        mock_torch.cuda.get_device_name.return_value = "Test GPU"
        mock_torch.cuda.get_device_capability.return_value = (8, 0)
        
        def mock_import(name, *args):
            if name == "torch":
                return mock_torch
            return __builtins__.__import__(name, *args)
        
        with patch("builtins.__import__", side_effect=mock_import):
            detector = DeviceDetector()
            
            assert detector.get_device() == "cuda"


class TestDeviceDetector:
    """Test suite for DeviceDetector functionality."""

    def test_when_get_device_then_returns_string(self):
        """Test that get_device() returns a valid device string."""
        detector = DeviceDetector()
        device = detector.get_device()
        assert isinstance(device, str)
        assert device in ["cpu", "cuda"]

    def test_when_multiple_instances_then_same_values(self):
        """Test that multiple DeviceDetector instances have consistent values."""
        detector1 = DeviceDetector()
        detector2 = DeviceDetector()

        
        # Both should return the same device
        assert detector1.get_device() == detector2.get_device()


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

    def test_when_stanza_engine_initializes_then_sets_device(self):
        """Test that StanzaNlpEngine correctly sets device from device_detector."""
        from presidio_analyzer.nlp_engine import StanzaNlpEngine
        
        engine = StanzaNlpEngine(
            models=[{"lang_code": "en", "model_name": "en"}]
        )
        
        # device should match device_detector
        expected_device = device_detector.get_device()
        assert engine.device == expected_device

    def test_when_gliner_recognizer_initializes_then_uses_correct_device(self):
        """Test that GLiNERRecognizer uses device from device_detector."""
        pytest.importorskip("gliner")
        from presidio_analyzer.predefined_recognizers import GLiNERRecognizer
        
        recognizer = GLiNERRecognizer()
        
        # map_location should match device_detector.get_device()
        assert recognizer.map_location == device_detector.get_device()

    def test_when_stanza_engine_device_matches_device_detector(self):
        """Test that StanzaNlpEngine.device matches device_detector."""
        from presidio_analyzer.nlp_engine import StanzaNlpEngine
        
        engine = StanzaNlpEngine(
            models=[{"lang_code": "en", "model_name": "en"}]
        )
        
        expected_device = device_detector.get_device()
        assert engine.device == expected_device


class TestDeviceDetectorBehavior:
    """Test suite for DeviceDetector runtime behavior."""

    def test_when_creating_new_instance_then_device_consistent(self):
        """Test that new instances have consistent device detection."""
        detector1 = DeviceDetector()
        detector2 = DeviceDetector()
        
        # Both should detect the same device
        assert detector1.get_device() == detector2.get_device()