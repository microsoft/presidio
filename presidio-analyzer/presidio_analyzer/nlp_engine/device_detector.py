"""GPU/CPU device detection for Presidio NLP engines.

This module provides lazy device detection using module-level __getattr__.
Access via `device_detector` attribute which is lazily initialized on first use.

The device can be explicitly set via the PRESIDIO_DEVICE environment variable.
Any valid PyTorch device string is accepted (e.g., 'cpu', 'cuda', 'cuda:0', 'cuda:1').

If PRESIDIO_DEVICE is not set, automatic detection is performed.

Usage:
    from presidio_analyzer.nlp_engine.device_detector import device_detector
    device = device_detector.get_device()
"""

import logging
import os
import threading

logger = logging.getLogger("presidio-analyzer")

PRESIDIO_DEVICE_ENV_VAR = "PRESIDIO_DEVICE"

_detector_instance = None
_lock = threading.Lock()


class DeviceDetector:
    """Detect and expose PyTorch device availability.

    Device selection priority:
    1. PRESIDIO_DEVICE environment variable (any valid device string)
    2. Automatic detection: Prefer CUDA when available, otherwise CPU

    Note: MPS (Apple Silicon/Metal) is currently not supported.
    """

    def __init__(self) -> None:
        self._device = self._get_device_from_env() or self._detect()
        logger.info(f"Using device of type: {self._device}")

    def _get_device_from_env(self) -> str | None:
        """Get device from PRESIDIO_DEVICE environment variable.

        Returns:
            Device string if env var is set, None otherwise.
        """
        env_device = os.environ.get(PRESIDIO_DEVICE_ENV_VAR, "").strip()
        if not env_device:
            return None

        logger.info(f"Device set to '{env_device}' via {PRESIDIO_DEVICE_ENV_VAR}")
        return env_device

    def _detect(self) -> str:
        """Auto-detect PyTorch CUDA support.

        Returns:
            'cuda' if available, 'cpu' otherwise.
        """
        try:
            import torch
        except ImportError:
            # torch not installed - this is expected, silently fall back to CPU
            return "cpu"

        try:
            if torch.cuda.is_available():
                _ = str(torch.tensor([1.0], device="cuda"))
                _ = torch.cuda.get_device_name(0)
                torch.cuda.get_device_capability(0)
                torch.cuda.empty_cache()
                return "cuda"
        except Exception as e:
            logger.warning(f"CUDA device detection failed, falling back to CPU: {e}")

        return "cpu"

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
