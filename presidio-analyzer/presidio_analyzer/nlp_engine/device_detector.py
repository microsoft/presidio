"""GPU/CPU device detection for Presidio NLP engines.

This module provides lazy device detection using module-level __getattr__.
Access via `device_detector` attribute which is lazily initialized on first use.

Usage:
    from presidio_analyzer.nlp_engine.device_detector import device_detector
    device = device_detector.get_device()
"""

import logging
import threading

logger = logging.getLogger("presidio-analyzer")

_detector_instance = None
_lock = threading.Lock()


class DeviceDetector:
    """Detect and expose PyTorch device availability.

    Prefer CUDA when available (Linux/Windows/NVIDIA),
    otherwise fall back to CPU.

    Note: MPS (Apple Silicon/Metal) is currently not supported.
    """

    def __init__(self) -> None:
        self._device = "cpu"
        self._detect()
        logger.info(f"Using device of type: {self._device}")

    def _detect(self) -> None:
        """Detect PyTorch CUDA support once."""
        try:
            import torch
        except ImportError:
            # torch not installed - this is expected, silently fall back to CPU
            return

        try:
            if torch.cuda.is_available():
                _ = str(torch.tensor([1.0], device="cuda"))
                _ = torch.cuda.get_device_name(0)
                torch.cuda.get_device_capability(0)
                torch.cuda.empty_cache()
                self._device = "cuda"
        except Exception as e:
            logger.warning(f"CUDA device detection failed, falling back to CPU: {e}")

    def get_device(self) -> str:
        """Return device string ('cuda' or 'cpu')."""
        return self._device


def __getattr__(name: str):
    """Lazily initialize device_detector on first access."""
    if name == "device_detector":
        global _detector_instance
        if _detector_instance is None:
            with _lock:
                _detector_instance = _detector_instance or DeviceDetector()
        return _detector_instance
    raise AttributeError(f"module {__name__} has no attribute {name}")
