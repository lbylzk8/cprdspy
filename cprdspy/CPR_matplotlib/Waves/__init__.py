"""Waves 模块 — 波形图案。

公开 API:
    - wave      统一波形函数（含 ax 参数）
    - wave_wave 简化波形函数
    - wave_ari  等差波形
    - wave_geo  等比波形
"""

from .waves import (
    wave,
    wave_wave,
    wave_ari,
    wave_geo,
)

__all__ = [
    "wave",
    "wave_wave",
    "wave_ari",
    "wave_geo",
]
