from __future__ import annotations

import numpy as np

from . import exit_code
from .errors import PdiError


def _require_grayscale(image: np.ndarray, operation: str) -> None:
    if image.ndim != 2:
        raise PdiError(
            exit_code.GENERAL_ERROR,
            f"A operacao '{operation}' exige uma imagem em escala de cinza (1 canal).",
        )


def _saturate(value: float) -> int:
    if value < 0:
        return 0
    if value > 255:
        return 255
    return int(value)


def apply_brightness(image: np.ndarray, value: int) -> np.ndarray:
    """g(x, y) = f(x, y) + value."""

    _require_grayscale(image, "brightness")
    height, width = image.shape
    output = np.empty((height, width), dtype=np.uint8)
    for y in range(height):
        for x in range(width):
            output[y, x] = _saturate(int(image[y, x]) + value)
    return output


def apply_contrast(image: np.ndarray, alpha: float) -> np.ndarray:
    """g(x, y) = alpha * (f(x, y) - 128) + 128."""

    _require_grayscale(image, "contrast")
    height, width = image.shape
    output = np.empty((height, width), dtype=np.uint8)
    for y in range(height):
        for x in range(width):
            transformed = alpha * (int(image[y, x]) - 128) + 128
            output[y, x] = _saturate(round(transformed))
    return output


def apply_negative(image: np.ndarray) -> np.ndarray:
    """g(x, y) = 255 - f(x, y)."""

    _require_grayscale(image, "negative")
    height, width = image.shape
    output = np.empty((height, width), dtype=np.uint8)
    for y in range(height):
        for x in range(width):
            output[y, x] = 255 - int(image[y, x])
    return output


def apply_threshold(image: np.ndarray, threshold: int) -> np.ndarray:
    """g(x, y) = 0 se f(x, y) < threshold, senao 255."""

    _require_grayscale(image, "threshold")
    height, width = image.shape
    output = np.empty((height, width), dtype=np.uint8)
    for y in range(height):
        for x in range(width):
            output[y, x] = 0 if int(image[y, x]) < threshold else 255
    return output


def compute_histogram(image: np.ndarray) -> list[int]:
    """Conta quantos pixels possuem cada intensidade entre 0 e 255."""

    _require_grayscale(image, "histogram")
    counts = [0] * 256
    height, width = image.shape
    for y in range(height):
        for x in range(width):
            counts[int(image[y, x])] += 1
    return counts
