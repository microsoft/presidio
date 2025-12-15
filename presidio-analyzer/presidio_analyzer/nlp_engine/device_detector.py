"""GPU/CPU device detection for Presidio NLP engines.

This module creates a single, process-wide DeviceDetector instance.
Consumers may import and use the shared instance directly.

The detector is initialized once at import time and is intended to be
read-only in practice.
"""

import logging
from typing import Optional

logger = logging.getLogger("presidio-analyzer")


class DeviceDetector:
    """Detect and expose PyTorch GPU/CPU availability.

    This class performs a one-time detection of CUDA availability and
    exposes the result for reuse across the process.
    """

    def __init__(self) -> None:
        self._device = "cpu"
        self._device_name: Optional[str] = None
        self._detect()

    def _detect(self) -> None:
        """Detect PyTorch CUDA support once."""
        try:
            import torch

            if torch.cuda.is_available():
                logger.info("GPU found, attempting CUDA initialization")
                try:
                    # Force CUDA initialization
                    _ = str(torch.tensor([1.0], device="cuda"))
                    self._device_name = torch.cuda.get_device_name(0)
                    torch.cuda.get_device_capability(0)
                    torch.cuda.empty_cache()

                    self._device = "cuda"
                    logger.info(
                        "CUDA available. Device: %s",
                        self._device_name,
                    )
                except Exception as e:
                    logger.warning(
                        "PyTorch CUDA initialization failed, falling back to CPU: %s",
                        e,
                    )
        except ImportError:
            logger.info("PyTorch not available, using CPU")

    def get_device(self) -> str:
        """Return device string ('cuda' or 'cpu')."""
        return self._device

    def get_gpu_device_name(self) -> Optional[str]:
        """Return GPU device name if available."""
        return self._device_name


# Shared, process-wide instance
device_detector = DeviceDetector()
