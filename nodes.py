"""ComfyUI node definitions for the official IndexTTS 2.5 model.

This plugin vendors the official index-tts codebase and exposes a small set of
nodes to drive IndexTTS-2.5 inference from a ComfyUI graph.
"""

from __future__ import annotations

import logging

import torch
from comfy_api.latest import io
from typing_extensions import override

from .runtime.inference_adapter import run_inference
from .runtime.audio_normalizer import OUTPUT_NORMALIZATION_MODES
from .runtime.types import EmotionConfig, ModelHandle, SamplingConfig
from .services.model_store import (
    MISSING_MODEL_OPTION,
    load_manifest,
    model_fingerprint,
    model_options,
    register_model_paths,
    resolve_model,
    validate_model_dir,
)


LOGGER = logging.getLogger("ComfyUI-IndexTTS2.5")
# 顶层分组名与插件目录名保持一致，避免前端对带点的目录名做截断显示。
CATEGORY = "Comfyui-indextts25-xzg/IndexTTS 2.5"
ModelType = io.Custom("XZG_INDEXTTS25_MODEL")
EmotionType = io.Custom("XZG_INDEXTTS25_EMOTION")
SamplingType = io.Custom("XZG_INDEXTTS25_SAMPLING")

# The 8 official IndexTTS-2.5 emotion dimensions.
EMOTION_VECTOR_NAMES = ("happy", "angry", "sad", "afraid", "disgusted", "melancholic", "surprised", "calm")
EMOTION_VECTOR_LABELS = (
    "Happy",
    "Angry",
    "Sad",
    "Afraid",
    "Disgusted",
    "Melancholic",
    "Surprised",
    "Calm",
)


def _device_options() -> list[str]:
    values = ["auto"]
    if torch.cuda.is_available():
        values.extend(f"cuda:{index}" for index in range(torch.cuda.device_count()))
    values.append("cpu")
    return values


def _resolve_device(requested: str) -> str:
    if requested != "auto":
        if requested.startswith("cuda") and not torch.cuda.is_available():
            raise RuntimeError("当前 ComfyUI 的 PyTorch 未检测到 CUDA。")
        return requested
    try:
        import comfy.model_management

        selected = str(comfy.model_management.get_torch_device())
    except Exception:
        selected = "cuda:0" if torch.cuda.is_available() else "cpu"
    if selected == "cuda":
        selected = f"cuda:{torch.cuda.current_device()}"
    if not (selected.startswith("cuda") or selected.startswith("cpu") or selected.startswith("xpu") or selected.startswith("mps")):
        raise RuntimeError(f"IndexTTS 2.5 暂不支持 ComfyUI 当前设备：{selected}")
    return selected


def _use_bf16(precision: str, device: str) -> bool:
    if precision == "float32":
        return False
    if precision == "bfloat16":
        if device == "cpu" or device.startswith("mps"):
            raise RuntimeError("bfloat16 仅建议在支持该格式的 CUDA/XPU 设备上使用。")
        return True
    if device.startswith("cuda"):
        index = int(device.split(":", 1)[1]) if ":" in device else torch.cuda.current_device()
        try:
            return bool(torch.cuda.is_bf16_supported(index))
        except TypeError:
            with torch.cuda.device(index):
                return bool(torch.cuda.is_bf16_supported())
    return device.startswith("xpu")


class IndexTTS25ModelLoader(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        options = model_options()
        return io.Schema(
            node_id="XZG_IndexTTS25_ModelLoader",
            display_name="IndexTTS 2.5 Model Loader",
            category=CATEGORY,
            search_aliases=["IndexTTS 2.5", "TTS model loader", "Voice Clone"],
            description="Discover and validate the IndexTTS 2.5 model under ComfyUI/models/TTS; weights are loaded on demand at first generation.",
            inputs=[
                io.Combo.Input(
                    "model_name",
                    display_name="IndexTTS 2.5 Model",
                    options=options,
                    default=options[0],
                    tooltip="Standard location: ComfyUI/models/TTS/IndexTTS-2.5. Refresh/restart ComfyUI after installing a model.",
                ),
                io.Combo.Input(
                    "device",
                    display_name="Device",
                    options=_device_options(),
                    default="auto",
                ),
                io.Combo.Input(
                    "precision",
                    display_name="Precision",
                    options=["auto", "bfloat16", "float32"],
                    default="auto",
                    tooltip="auto uses bfloat16 on supported GPUs, otherwise float32.",
                ),
                io.Boolean.Input(
                    "use_qwen_emo",
                    display_name="Enable Text Emotion Analysis",
                    default=False,
                    tooltip=(
                        "Loads the Qwen emotion model (extra VRAM) to enable the emotion "
                        "control node's text description mode. Keep off if you don't use it."
                    ),
                ),
                io.Boolean.Input(
                    "use_cuda_kernel",
                    display_name="BigVGAN CUDA Fused Kernel",
                    default=False,
                    advanced=True,
                    tooltip="May compile an extension on first use; keep off if unsure.",
                ),
                io.Boolean.Input(
                    "release_after_run",
                    display_name="Release Model After Run",
                    default=False,
                    advanced=True,
                    tooltip="Suitable for low-VRAM environments; lowers speed for consecutive generations.",
                ),
                io.Boolean.Input(
                    "verify_hashes",
                    display_name="Full SHA-256 Verification",
                    default=False,
                    advanced=True,
                    tooltip="First verification reads ~5GB of files; otherwise only file sizes are checked.",
                ),
                io.String.Input(
                    "custom_model_path",
                    display_name="Custom Model Absolute Path",
                    default="",
                    optional=True,
                    advanced=True,
                    tooltip="Leave empty to use the list above; only for existing complete IndexTTS 2.5 directories.",
                ),
            ],
            outputs=[
                ModelType.Output("model", display_name="IndexTTS 2.5 Model"),
            ],
        )

    @classmethod
    def fingerprint_inputs(
        cls,
        model_name: str,
        device: str,
        precision: str,
        use_qwen_emo: bool,
        use_cuda_kernel: bool,
        release_after_run: bool,
        verify_hashes: bool,
        custom_model_path: str = "",
    ) -> str:
        try:
            path = resolve_model(model_name, custom_model_path)
            return f"{model_fingerprint(path)}|qwen={int(bool(use_qwen_emo))}"
        except Exception as exc:
            return f"missing:{model_name}:{custom_model_path}:{exc}"

    @classmethod
    def validate_inputs(cls, model_name: str, custom_model_path: str = "", **kwargs) -> bool | str:
        if model_name == MISSING_MODEL_OPTION and not custom_model_path.strip():
            return "未找到 IndexTTS 2.5 模型；请先运行 scripts/download_models.py。"
        return True

    @classmethod
    def execute(
        cls,
        model_name: str,
        device: str,
        precision: str,
        use_qwen_emo: bool,
        use_cuda_kernel: bool,
        release_after_run: bool,
        verify_hashes: bool,
        custom_model_path: str = "",
    ) -> io.NodeOutput:
        model_dir = resolve_model(model_name, custom_model_path)
        report = validate_model_dir(model_dir, verify_hashes=verify_hashes)
        report.require_valid()
        resolved_device = _resolve_device(device)
        manifest = load_manifest()
        handle = ModelHandle(
            model_dir=model_dir,
            device=resolved_device,
            use_bf16=_use_bf16(precision, resolved_device),
            use_cuda_kernel=bool(use_cuda_kernel and resolved_device.startswith("cuda")),
            release_after_run=bool(release_after_run),
            model_revision=str(manifest["modelRevision"]),
            use_qwen_emo=bool(use_qwen_emo),
        )
        return io.NodeOutput(handle)


def _strength_input() -> io.Float.Input:
    return io.Float.Input(
        "strength",
        display_name="Emotion Strength",
        default=1.0,
        min=0.0,
        max=1.0,
        step=0.01,
        display_mode=io.NumberDisplay.slider,
    )


class IndexTTS25EmotionControl(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        vector_inputs = [
            io.Float.Input(name, display_name=label, default=0.0, min=0.0, max=1.2, step=0.01)
            for name, label in zip(EMOTION_VECTOR_NAMES, EMOTION_VECTOR_LABELS)
        ]
        vector_inputs.extend(
            [
                _strength_input(),
                io.Boolean.Input(
                    "use_random",
                    display_name="Random Emotion Prototype",
                    default=False,
                    tooltip="When on, the seed determines the prototype for each emotion; when off, matches the voice reference.",
                ),
            ]
        )
        return io.Schema(
            node_id="XZG_IndexTTS25_EmotionControl",
            display_name="IndexTTS 2.5 Emotion Control",
            category=CATEGORY,
            search_aliases=["IndexTTS emotion", "Emotion vector", "Emotion reference audio", "Happy", "Angry", "Sad"],
            description=(
                "Control emotion in four ways: 8-dimensional vector, emotion reference audio, text description, or follow the voice."
                "The official model ships with 8 emotion dimensions (Happy/Angry/Sad/Afraid/Disgusted/Melancholic/Surprised/Calm)."
            ),
            inputs=[
                io.DynamicCombo.Input(
                    "mode",
                    display_name="Emotion Mode",
                    options=[
                        io.DynamicCombo.Option("vector", vector_inputs),
                        io.DynamicCombo.Option(
                            "reference_audio",
                            [
                                io.Audio.Input("emotion_audio", display_name="Emotion Reference Audio"),
                                _strength_input(),
                            ],
                        ),
                        io.DynamicCombo.Option(
                            "text",
                            [
                                io.String.Input(
                                    "emotion_text",
                                    display_name="Emotion Description",
                                    multiline=True,
                                    default="",
                                    placeholder=(
                                        "例如：高兴——语速轻快、带笑意；悲伤——语速缓慢、声音微颤；"
                                        "低沉压抑，略带忧郁；惊讶又兴奋地大喊。留空则分析待合成文本。"
                                    ),
                                ),
                                _strength_input(),
                            ],
                        ),
                        io.DynamicCombo.Option("speaker", []),
                    ],
                    tooltip="text loads an additional Qwen emotion model on demand.",
                ),
            ],
            outputs=[
                EmotionType.Output("emotion", display_name="Emotion Control"),
            ],
        )

    @classmethod
    def execute(cls, mode: dict) -> io.NodeOutput:
        selected = str(mode["mode"])
        if selected == "speaker":
            config = EmotionConfig(mode="speaker")
        elif selected == "reference_audio":
            config = EmotionConfig(
                mode="reference_audio",
                reference_audio=mode["emotion_audio"],
                strength=float(mode.get("strength", 1.0)),
            )
        elif selected == "vector":
            names = EMOTION_VECTOR_NAMES
            values = [max(0.0, min(1.2, float(mode.get(name, 0.0)))) for name in names]
            notes: list[str] = []
            total = sum(values)
            if total > 0.8:
                scale = 0.8 / total
                values = [value * scale for value in values]
                notes.append("向量总强度超过 0.8，已等比归一化")
            config = EmotionConfig(
                mode="vector",
                vector=tuple(values),
                strength=float(mode.get("strength", 1.0)),
                use_random=bool(mode.get("use_random", False)),
                notes=tuple(notes),
            )
        elif selected == "text":
            emotion_text = str(mode.get("emotion_text", "")).strip()
            config = EmotionConfig(
                mode="text",
                text=emotion_text or None,
                strength=float(mode.get("strength", 1.0)),
            )
        else:
            raise ValueError(f"未知情感模式：{selected}")
        return io.NodeOutput(config)


class IndexTTS25SamplingConfig(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="XZG_IndexTTS25_SamplingConfig",
            display_name="IndexTTS 2.5 Sampling Config",
            category=CATEGORY,
            search_aliases=["IndexTTS sampling", "TTS sampling config"],
            description="Centrally configure determinism, sampling, long-text segmentation, pauses and text normalization parameters.",
            inputs=[
                io.Boolean.Input(
                    "do_sample",
                    display_name="Enable Random Sampling",
                    default=False,
                    tooltip="Results are more stable when off; temperature/top_p/top_k take effect when on.",
                ),
                io.Float.Input("temperature", display_name="temperature", default=0.8, min=0.1, max=2.0, step=0.05, advanced=True),
                io.Float.Input("top_p", display_name="top_p", default=0.8, min=0.05, max=1.0, step=0.01, advanced=True),
                io.Int.Input("top_k", display_name="top_k", default=30, min=0, max=200, step=1, advanced=True),
                io.Int.Input("num_beams", display_name="num_beams", default=3, min=1, max=10, step=1, advanced=True),
                io.Float.Input(
                    "repetition_penalty",
                    display_name="repetition_penalty",
                    default=10.0,
                    min=0.1,
                    max=20.0,
                    step=0.1,
                    advanced=True,
                ),
                io.Float.Input("length_penalty", display_name="length_penalty", default=0.0, min=-2.0, max=2.0, step=0.05, advanced=True),
                io.Int.Input("max_mel_tokens", display_name="Max Mel Tokens", default=1500, min=256, max=4096, step=16, advanced=True),
                io.Int.Input(
                    "max_text_tokens_per_segment",
                    display_name="Max Text Tokens per Segment",
                    default=120,
                    min=20,
                    max=300,
                    step=5,
                ),
                io.Int.Input("segment_silence_ms", display_name="Segment Silence (ms)", default=200, min=0, max=3000, step=10),
                io.Boolean.Input("text_normalization", display_name="Text Normalization", default=True),
            ],
            outputs=[
                SamplingType.Output("sampling", display_name="Sampling Config"),
                io.String.Output("sampling_info", display_name="Sampling Info"),
            ],
        )

    @classmethod
    def execute(
        cls,
        do_sample: bool,
        temperature: float,
        top_p: float,
        top_k: int,
        num_beams: int,
        repetition_penalty: float,
        length_penalty: float,
        max_mel_tokens: int,
        max_text_tokens_per_segment: int,
        segment_silence_ms: int,
        text_normalization: bool,
    ) -> io.NodeOutput:
        config = SamplingConfig(
            do_sample=bool(do_sample),
            temperature=float(temperature),
            top_p=float(top_p),
            top_k=int(top_k),
            num_beams=int(num_beams),
            repetition_penalty=float(repetition_penalty),
            length_penalty=float(length_penalty),
            max_mel_tokens=int(max_mel_tokens),
            max_text_tokens_per_segment=int(max_text_tokens_per_segment),
            segment_silence_ms=int(segment_silence_ms),
            text_normalization=bool(text_normalization),
        )
        mode = "随机采样" if config.do_sample else "确定性/束搜索"
        info = (
            f"{mode} | beams={config.num_beams} | max_mel={config.max_mel_tokens} | "
            f"segment_tokens={config.max_text_tokens_per_segment} | silence={config.segment_silence_ms}ms"
        )
        return io.NodeOutput(config, info)


class IndexTTS25Generate(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="XZG_IndexTTS25_Generate",
            display_name="IndexTTS 2.5 Speech Generation",
            category=CATEGORY,
            essentials_category="Audio",
            search_aliases=["IndexTTS TTS", "voice clone", "Voice Clone"],
            description="Multilingual zero-shot voice cloning with the IndexTTS 2.5 model, outputting standard ComfyUI AUDIO.",
            inputs=[
                ModelType.Input("model", display_name="IndexTTS 2.5 Model"),
                io.Audio.Input("speaker_audio", display_name="Speaker Reference Audio"),
                io.String.Input(
                    "text",
                    display_name="Text to Synthesize",
                    multiline=True,
                    default="Welcome to IndexTTS 2.5.",
                    dynamic_prompts=True,
                ),
                io.Combo.Input(
                    "language",
                    display_name="Language",
                    options=["ZH", "EN", "JA", "ES", "AR"],
                    default="ZH",
                ),
                io.Float.Input(
                    "duration_factor",
                    display_name="Duration Factor (smaller = faster)",
                    default=1.0,
                    min=0.5,
                    max=2.0,
                    step=0.05,
                    display_mode=io.NumberDisplay.slider,
                ),
                io.Int.Input(
                    "seed",
                    display_name="seed",
                    default=0,
                    min=0,
                    max=0xFFFFFFFFFFFFFFFF,
                    control_after_generate=True,
                ),
                EmotionType.Input(
                    "emotion",
                    display_name="Emotion Control",
                    optional=True,
                    tooltip="Follows the voice reference when not connected.",
                ),
                SamplingType.Input(
                    "sampling",
                    display_name="Sampling Config",
                    optional=True,
                    tooltip="Uses stable defaults when not connected.",
                ),
                io.Combo.Input(
                    "output_normalization",
                    display_name="Output Normalization",
                    options=list(OUTPUT_NORMALIZATION_MODES),
                    default=OUTPUT_NORMALIZATION_MODES[0],
                    advanced=True,
                    tooltip=(
                        "match reference: the output is scaled to the same gated-RMS level as "
                        "the speaker reference audio you fed in (loud in = loud out). "
                        "rms -16 dB: fixed broadcast level with -1 dB peak ceiling. "
                        "peak -1 dB: peak normalization only. off: raw model output."
                    ),
                ),
            ],
            outputs=[
                io.Audio.Output("audio", display_name="Generated Audio"),
            ],
        )

    @classmethod
    def validate_inputs(cls, text: str, duration_factor: float, **kwargs) -> bool | str:
        if not str(text).strip():
            return "待合成文本不能为空。"
        if not 0.5 <= float(duration_factor) <= 2.0:
            return "时长系数必须在 0.5 到 2.0 之间。"
        return True

    @classmethod
    def execute(
        cls,
        model: ModelHandle,
        speaker_audio: dict,
        text: str,
        language: str,
        duration_factor: float,
        seed: int,
        emotion: EmotionConfig | None = None,
        sampling: SamplingConfig | None = None,
        output_normalization: str = OUTPUT_NORMALIZATION_MODES[0],
    ) -> io.NodeOutput:
        audio, _ = run_inference(
            handle=model,
            speaker_audio=speaker_audio,
            text=text,
            language=language,
            duration_factor=duration_factor,
            seed=seed,
            emotion=emotion,
            sampling=sampling,
            output_normalization=output_normalization,
        )
        return io.NodeOutput(audio)
