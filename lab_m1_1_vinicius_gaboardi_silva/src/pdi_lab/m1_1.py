"""Algoritmos do Laboratorio M1.1 — representacao, canais e niveis de cinza.

Todas as operacoes percorrem os pixels manualmente (loops explicitos), como
exigido pelo roteiro. As unicas chamadas prontas usadas aqui sao consultas de
infraestrutura ja autorizadas pelo contrato tecnico (shape, dtype, criacao de
matrizes com numpy.zeros/empty).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from . import exit_code
from .errors import PdiError

# Indices dos canais na ordem em que o OpenCV carrega imagens coloridas (BGR).
_BLUE, _GREEN, _RED = 0, 1, 2
_CHANNEL_NAMES = {_BLUE: "b", _GREEN: "g", _RED: "r"}


def _channel_count(image: np.ndarray) -> int:
    return 1 if image.ndim == 2 else image.shape[2]


def _require_channels(image: np.ndarray, expected: int, operation: str) -> None:
    actual = _channel_count(image)
    if actual != expected:
        raise PdiError(
            exit_code.GENERAL_ERROR,
            f"A operacao '{operation}' espera uma imagem com {expected} canal(is), "
            f"mas a entrada possui {actual}.",
        )


@dataclass(frozen=True)
class ChannelStats:
    minimum: int
    maximum: int
    mean: float


@dataclass(frozen=True)
class ImageStats:
    width: int
    height: int
    channels: int
    dtype: str
    pixel_count: int
    overall: ChannelStats
    per_channel: dict[str, ChannelStats] = field(default_factory=dict)


def inspect_image(image: np.ndarray) -> ImageStats:
    """Percorre a imagem manualmente para calcular dimensoes e estatisticas."""

    height, width = image.shape[0], image.shape[1]
    channels = _channel_count(image)

    overall_min = None
    overall_max = None
    overall_sum = 0
    overall_count = 0

    per_channel_min = [None] * channels
    per_channel_max = [None] * channels
    per_channel_sum = [0] * channels
    per_channel_count = [0] * channels

    for y in range(height):
        for x in range(width):
            if channels == 1:
                values = (int(image[y, x]),)
            else:
                values = tuple(int(image[y, x, c]) for c in range(channels))

            for c, value in enumerate(values):
                if per_channel_min[c] is None or value < per_channel_min[c]:
                    per_channel_min[c] = value
                if per_channel_max[c] is None or value > per_channel_max[c]:
                    per_channel_max[c] = value
                per_channel_sum[c] += value
                per_channel_count[c] += 1

                if overall_min is None or value < overall_min:
                    overall_min = value
                if overall_max is None or value > overall_max:
                    overall_max = value
                overall_sum += value
                overall_count += 1

    overall = ChannelStats(
        minimum=overall_min if overall_min is not None else 0,
        maximum=overall_max if overall_max is not None else 0,
        mean=(overall_sum / overall_count) if overall_count else 0.0,
    )

    per_channel: dict[str, ChannelStats] = {}
    if channels > 1:
        for c in range(channels):
            name = _CHANNEL_NAMES.get(c, str(c))
            per_channel[name] = ChannelStats(
                minimum=per_channel_min[c],
                maximum=per_channel_max[c],
                mean=per_channel_sum[c] / per_channel_count[c],
            )

    return ImageStats(
        width=width,
        height=height,
        channels=channels,
        dtype=str(image.dtype),
        pixel_count=width * height,
        overall=overall,
        per_channel=per_channel,
    )


def copy_image(image: np.ndarray) -> np.ndarray:
    """Copia a imagem pixel a pixel, sem usar image.copy()/np.copy()."""

    height, width = image.shape[0], image.shape[1]
    channels = _channel_count(image)
    output = np.zeros_like(image)

    for y in range(height):
        for x in range(width):
            if channels == 1:
                output[y, x] = image[y, x]
            else:
                for c in range(channels):
                    output[y, x, c] = image[y, x, c]

    return output


def extract_channel(image: np.ndarray, channel: int) -> np.ndarray:
    """Preserva um unico canal (BGR) e zera os demais, pixel a pixel."""

    _require_channels(image, 3, f"channel_{_CHANNEL_NAMES.get(channel, channel)}")

    height, width = image.shape[0], image.shape[1]
    output = np.zeros_like(image)

    for y in range(height):
        for x in range(width):
            output[y, x, channel] = image[y, x, channel]

    return output


def grayscale_average(image: np.ndarray) -> np.ndarray:
    """g = (R + G + B) / 3, calculado e arredondado pixel a pixel."""

    _require_channels(image, 3, "grayscale_average")

    height, width = image.shape[0], image.shape[1]
    output = np.zeros((height, width), dtype=np.uint8)

    for y in range(height):
        for x in range(width):
            blue = int(image[y, x, _BLUE])
            green = int(image[y, x, _GREEN])
            red = int(image[y, x, _RED])
            value = (red + green + blue) / 3.0
            output[y, x] = min(255, max(0, round(value)))

    return output


def grayscale_weighted(image: np.ndarray) -> np.ndarray:
    """g = 0.299R + 0.587G + 0.114B, calculado e arredondado pixel a pixel."""

    _require_channels(image, 3, "grayscale_weighted")

    height, width = image.shape[0], image.shape[1]
    output = np.zeros((height, width), dtype=np.uint8)

    for y in range(height):
        for x in range(width):
            blue = int(image[y, x, _BLUE])
            green = int(image[y, x, _GREEN])
            red = int(image[y, x, _RED])
            value = 0.299 * red + 0.587 * green + 0.114 * blue
            output[y, x] = min(255, max(0, round(value)))

    return output


def quantize_image(image: np.ndarray, levels: int) -> np.ndarray:
    """Reduz a resolucao radiometrica para `levels` niveis igualmente espacados.

    Cada pixel e mapeado para o inicio da faixa (bin) em que ele cai:
    faixa = 256 / levels; saida = (entrada // faixa) * faixa.
    O resultado permanece sempre dentro de [0, 255].
    """

    if levels not in {2, 4, 8, 16}:
        raise PdiError(
            exit_code.INVALID_PARAMETER,
            "--levels deve ser 2, 4, 8 ou 16.",
        )

    step = 256 // levels
    height, width = image.shape[0], image.shape[1]
    channels = _channel_count(image)
    output = np.zeros_like(image)

    for y in range(height):
        for x in range(width):
            if channels == 1:
                value = int(image[y, x])
                output[y, x] = min(255, (value // step) * step)
            else:
                for c in range(channels):
                    value = int(image[y, x, c])
                    output[y, x, c] = min(255, (value // step) * step)

    return output
