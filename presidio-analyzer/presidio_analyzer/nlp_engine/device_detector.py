"""GPU/CPU device detection for Presidio NLP engines.

This module creates a single, process-wide DeviceDetector instance.
Consumers may import and use the shared instance directly.

The detector is initialized once at import time and is intended to be
read-only in practice.
"""

import logging

logger = logging.getLogger("presidio-analyzer")


class DeviceDetector:
    """Detect and expose PyTorch device availability.

    Prefer CUDA when available (Linux/Windows/NVIDIA),
    otherwise use MPS on macOS (Apple Silicon),
    otherwise fall back to CPU.
    """

    def __init__(self) -> None:
        self._device = "cpu"
        self._detect()
        logger.info(f"Using device of type: {self._device}")

    def _detect(self) -> None:
        """Detect PyTorch CUDA/MPS support once."""
        try:
            import torch
        except ImportError:
            logger.info("PyTorch not available, using CPU")
            return

        # 1) CUDA (NVIDIA)
        if torch.cuda.is_available():
            try:
                _ = str(torch.tensor([1.0], device="cuda"))
                _ = torch.cuda.get_device_name(0)
                torch.cuda.get_device_capability(0)
                torch.cuda.empty_cache()
                self._device = "cuda"
                return
            except Exception as e:
                logger.warning(f"PyTorch CUDA initialization failed, falling back: {e}")

        # 2) MPS (Apple Metal / macOS)
        if getattr(torch.backends, "mps", None) is not None:
            if torch.backends.mps.is_built() and torch.backends.mps.is_available():
                try:
                    _ = str(torch.tensor([1.0], device="mps"))
                    self._device = "mps"
                    return
                except Exception as e:
                    logger.warning(
                        f"PyTorch MPS initialization failed, falling back to CPU: {e}"
                    )

    def get_device(self) -> str:
        """Return device string ('cuda', 'mps', or 'cpu')."""
        return self._device


# Shared, process-wide instance
device_detector = DeviceDetector()
