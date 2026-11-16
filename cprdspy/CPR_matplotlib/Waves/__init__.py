"""Waves 模块 — 波形图案。

公开 API:
    - wave           统一波形函数（含 ax 参数）
    - wave_fill      统一波形函数（带填充）
    - wave_wave      简化波形函数
    - wave_wave_fill 简化波形函数（带填充）
    - wave_ari       等差波形
    - wave_ari_fill  等差波形（带填充）
    - wave_geo       等比波形
    - wave_geo_fill  等比波形（带填充）
"""

from .wave import (
    wave,
    wave_fill,
    wave_wave,
    wave_wave_fill,
    wave_ari,
    wave_ari_fill,
    wave_geo,
    wave_geo_fill,
)

__all__ = [
    "wave",
    "wave_fill",
    "wave_wave",
    "wave_wave_fill",
    "wave_ari",
    "wave_ari_fill",
    "wave_geo",
    "wave_geo_fill",
]
