"""GPU/CPU device detection singleton for Presidio NLP engines."""

import logging
import sys
from typing import Optional

logger = logging.getLogger("presidio-analyzer")


class DeviceDetector:
    """Singleton for GPU/CPU detection. Lazy initialization on first use."""

    _instance: Optional["DeviceDetector"] = None
    _torch_initialized: bool = False
    _has_torch_gpu: bool = False
    _torch_device: str = "cpu"
    _torch_device_name: Optional[str] = None

    def __new__(cls) -> "DeviceDetector":
        """Return singleton instance and detect torch GPU on first creation."""
        if cls._instance is None:
            cls._instance = super(DeviceDetector, cls).__new__(cls)
            cls._instance._detect_torch_gpu()
        return cls._instance

    def _detect_torch_gpu(self) -> None:
        """Detect PyTorch GPU/CUDA once."""
        if DeviceDetector._torch_initialized:
            return

        try:
            import torch

            if torch.cuda.is_available():
                logger.info("GPU found, attempting CUDA initialization")
                
                
                try:
                    # Force CUDA initialization
                    str(torch.tensor([1.0], device="cuda"))
                    DeviceDetector._torch_device_name = torch.cuda.get_device_name(0)
                    torch.cuda.get_device_capability(0)
                    torch.cuda.empty_cache()

                    DeviceDetector._has_torch_gpu = True
                    DeviceDetector._torch_device = "cuda"
                    logger.info(
                        f"GPU and CUDA available. Device: {DeviceDetector._torch_device_name}"
                    )
                        
                except Exception as e:
                    logger.warning(f"PyTorch Pre-Check: FAILED with error: {e}")
                    DeviceDetector._has_torch_gpu = False
                    DeviceDetector._torch_device = "cpu"
            else:
                logger.info("No GPU found, using CPU")
                DeviceDetector._has_torch_gpu = False
                DeviceDetector._torch_device = "cpu"

        except ImportError:
            logger.info("PyTorch not available, using CPU")
            DeviceDetector._has_torch_gpu = False
            DeviceDetector._torch_device = "cpu"

        DeviceDetector._torch_initialized = True


    def has_torch_gpu(self) -> bool:
        """Return True if PyTorch GPU is available."""
        return DeviceDetector._has_torch_gpu

    def get_torch_device(self) -> str:
        """Return torch device string: 'cuda:0' or 'cpu'."""
        return DeviceDetector._torch_device

    def get_torch_device_name(self) -> Optional[str]:
        """Return PyTorch GPU device name or None."""
        return DeviceDetector._torch_device_name

    def get_torch_device_info(self) -> dict:
        """Return PyTorch device information."""
        return {
            "has_gpu": DeviceDetector._has_torch_gpu,
            "device_name": DeviceDetector._torch_device_name,
            "device": DeviceDetector._torch_device,
        }


# Initialize singleton at module import to preload CUDA libraries if GPU available
DeviceDetector()
