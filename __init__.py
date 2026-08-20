"""ComfyUI IndexTTS 2.5 custom nodes (vendors the official index-tts codebase).

Provides nodes to run zero-shot voice cloning with the official IndexTTS-2.5
model, including emotion control, language selection and sampling controls.
"""

import logging
from typing_extensions import override

from comfy_api.latest import ComfyExtension

from .nodes import (
    IndexTTS25EmotionControl,
    IndexTTS25Generate,
    IndexTTS25ModelLoader,
    IndexTTS25SamplingConfig,
)
from .services.model_store import register_model_paths

LOGGER = logging.getLogger("ComfyUI-IndexTTS2.5")
__version__ = "2.0.1"


class IndexTTS25Extension(ComfyExtension):
    @override
    async def on_load(self) -> None:
        register_model_paths()
        LOGGER.info("Loaded ComfyUI IndexTTS 2.5 (XZG) nodes")

    @override
    async def get_node_list(self) -> list:
        return [
            IndexTTS25ModelLoader,
            IndexTTS25EmotionControl,
            IndexTTS25SamplingConfig,
            IndexTTS25Generate,
        ]


async def comfy_entrypoint() -> IndexTTS25Extension:
    return IndexTTS25Extension()


__all__ = [
    "IndexTTS25ModelLoader",
    "IndexTTS25EmotionControl",
    "IndexTTS25SamplingConfig",
    "IndexTTS25Generate",
    "IndexTTS25Extension",
    "comfy_entrypoint",
    "__version__",
]
