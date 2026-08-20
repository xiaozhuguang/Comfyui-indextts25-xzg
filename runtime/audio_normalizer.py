"""Loudness normalization for reference inputs and generated audio.

Implements a gated-RMS loudness estimate inspired by ITU-R BS.1770 gating:
audio is split into short frames and only frames above the silence floor
contribute, so leading/trailing silence does not drag the measurement down.
Pure torch/numpy — no extra dependencies, safe for offline environments.
"""

from __future__ import annotations

import math
from typing import Any

import torch


OUTPUT_NORMALIZATION_MODES = ("match reference", "rms -16 dB", "peak -1 dB", "off")

# Reference audio is normalized to this gated RMS level (dBFS) before caching.
REFERENCE_TARGET_DB = -20.0
REFERENCE_PEAK_CEILING_DB = -3.0
_REFERENCE_MAX_BOOST_DB = 12.0
_REFERENCE_MAX_CUT_DB = 24.0

_FRAME_SECONDS = 0.05
_SILENCE_FLOOR_DB = -60.0
_EPSILON = 1e-10


def _db_to_gain(db: float) -> float:
    return math.pow(10.0, db / 20.0)


def _gain_to_db(gain: float) -> float:
    return 20.0 * math.log10(max(gain, _EPSILON))


def remove_dc(waveform: torch.Tensor) -> torch.Tensor:
    return waveform - waveform.mean(dim=-1, keepdim=True)


def active_rms(waveform: torch.Tensor, sample_rate: int) -> float:
    """Gated RMS in linear scale; silent frames (< -60 dBFS) are excluded."""
    flat = waveform.reshape(-1).to(torch.float32)
    total = flat.numel()
    if total == 0:
        return 0.0
    frame = max(1, int(round(_FRAME_SECONDS * sample_rate)))
    usable = (total // frame) * frame
    if usable < frame:
        return max(float(torch.sqrt(flat.pow(2).mean())), 0.0)
    frames = flat[:usable].view(-1, frame)
    frame_rms = frames.pow(2).mean(dim=1).sqrt()
    floor = _db_to_gain(_SILENCE_FLOOR_DB)
    loud = frame_rms[frame_rms > floor]
    if loud.numel() == 0:
        return float(frame_rms.mean())
    return float(loud.pow(2).mean().sqrt())


def normalize_rms(
    waveform: torch.Tensor,
    sample_rate: int,
    *,
    target_db: float,
    max_boost_db: float = 12.0,
    max_cut_db: float = 24.0,
    peak_ceiling_db: float = -1.0,
) -> tuple[torch.Tensor, float]:
    """Scale toward the target gated-RMS level without exceeding the peak ceiling.

    Returns (audio, applied_gain_linear). Boosting is capped (a near-silent
    noisy source should not be amplified into pure noise) while attenuation is
    allowed further, since cutting level is always safe.
    """
    rms = active_rms(waveform, sample_rate)
    if rms <= _EPSILON:
        return waveform, 1.0
    gain = _db_to_gain(target_db) / rms
    gain = min(max(gain, _db_to_gain(-max_cut_db)), _db_to_gain(max_boost_db))
    peak = float(waveform.abs().max())
    ceiling = _db_to_gain(peak_ceiling_db)
    if peak > _EPSILON and peak * gain > ceiling:
        gain = ceiling / peak
    return waveform * gain, gain


def normalize_peak(waveform: torch.Tensor, *, target_db: float = -1.0) -> tuple[torch.Tensor, float]:
    peak = float(waveform.abs().max())
    if peak <= _EPSILON:
        return waveform, 1.0
    gain = _db_to_gain(target_db) / peak
    return waveform * gain, gain


def measure(waveform: torch.Tensor, sample_rate: int) -> tuple[float, float]:
    """Return (peak_dbfs, gated_rms_dbfs)."""
    peak = float(waveform.abs().max()) if waveform.numel() else 0.0
    rms = active_rms(waveform, sample_rate)
    return _gain_to_db(peak), _gain_to_db(rms)


def normalize_reference(waveform: torch.Tensor, sample_rate: int) -> tuple[torch.Tensor, float]:
    """Standardize a reference/speaker audio: DC removal + gated RMS + headroom."""
    cleaned = remove_dc(waveform)
    return normalize_rms(
        cleaned,
        sample_rate,
        target_db=REFERENCE_TARGET_DB,
        max_boost_db=_REFERENCE_MAX_BOOST_DB,
        max_cut_db=_REFERENCE_MAX_CUT_DB,
        peak_ceiling_db=REFERENCE_PEAK_CEILING_DB,
    )


def apply_output_normalization(
    audio: dict[str, Any],
    mode: str,
    *,
    reference_rms_db: float | None = None,
) -> tuple[dict[str, Any], str]:
    """Normalize a ComfyUI AUDIO dict according to the selected mode.

    Returns (audio, note); note is "" when disabled or nothing was measured.
    "match reference" scales the output to the gated RMS measured on the
    original (pre-normalization) speaker reference, so the generated voice is
    as loud as the audio the user fed in.
    """
    if mode not in OUTPUT_NORMALIZATION_MODES:
        raise ValueError(f"未知输出归一化模式：{mode}（可选：{', '.join(OUTPUT_NORMALIZATION_MODES)}）")
    if mode == "off":
        return audio, ""

    waveform = audio["waveform"]
    sample_rate = int(audio["sample_rate"])
    if mode == "match reference":
        target = float(reference_rms_db) if reference_rms_db is not None else REFERENCE_TARGET_DB
        normalized, gain = normalize_rms(
            waveform,
            sample_rate,
            target_db=target,
            max_boost_db=24.0,
            max_cut_db=24.0,
            peak_ceiling_db=-1.0,
        )
        label = f"对齐参考 {target:.0f}dB"
    elif mode == "rms -16 dB":
        normalized, gain = normalize_rms(
            waveform,
            sample_rate,
            target_db=-16.0,
            max_boost_db=20.0,
            max_cut_db=20.0,
            peak_ceiling_db=-1.0,
        )
        label = mode.replace(" dB", "dB")
    else:
        normalized, gain = normalize_peak(waveform, target_db=-1.0)
        label = mode.replace(" dB", "dB")
    normalized = normalized.clamp(-1.0, 1.0).to(torch.float32).contiguous()

    peak_db, rms_db = measure(normalized, sample_rate)
    note = f"输出归一化[{label}] gain={_gain_to_db(gain):+.1f}dB peak={peak_db:.1f}dBFS rms={rms_db:.1f}dBFS"
    return {**audio, "waveform": normalized}, note
