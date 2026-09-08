from __future__ import annotations

import sys

from . import exit_code
from .cli import CliOptions
from .image_io import read_image, write_image
from .m1_1 import (
    copy_image,
    extract_channel,
    grayscale_average,
    grayscale_weighted,
    inspect_image,
    quantize_image,
)
from .parameters import parameter_as_int
from .result_io import write_json_object


# A lista é equivalente às variantes C++ e Java. Atividades complementares
# dos roteiros não são transformadas em requisitos do contrato mínimo.
KNOWN_OPERATIONS = {
    # M1.1 — representação, canais e níveis de cinza
    "inspect",
    "copy",
    "channel_b",
    "channel_g",
    "channel_r",
    "grayscale_average",
    "grayscale_weighted",
    "quantize",

    # M1.2 — transformações de intensidade
    "brightness",
    "contrast",
    "negative",
    "threshold",
    "histogram",

    # M1.3 — convolução e filtragem espacial
    "convolution",
    "mean_filter",
    "weighted_mean",
    "laplacian",
    "sobel",
}


def is_known_operation(operation: str) -> bool:
    """Retorna True somente para as operações previstas no contrato comum."""

    return operation in KNOWN_OPERATIONS


# Índice do canal correspondente na ordem BGR usada pelo OpenCV.
_CHANNEL_INDEX = {"channel_b": 0, "channel_g": 1, "channel_r": 2}


def _print_inspect(stats) -> None:
    print(f"width={stats.width}")
    print(f"height={stats.height}")
    print(f"channels={stats.channels}")
    print(f"pixels={stats.pixel_count}")
    print(f"type={stats.dtype}")
    print(f"min={stats.overall.minimum}")
    print(f"max={stats.overall.maximum}")
    print(f"mean={stats.overall.mean:.4f}")
    for name, channel_stats in stats.per_channel.items():
        print(f"channel_{name}_min={channel_stats.minimum}")
        print(f"channel_{name}_max={channel_stats.maximum}")
        print(f"channel_{name}_mean={channel_stats.mean:.4f}")


def _inspect_as_dict(stats) -> dict[str, str]:
    values = {
        "width": stats.width,
        "height": stats.height,
        "channels": stats.channels,
        "pixels": stats.pixel_count,
        "type": stats.dtype,
        "min": stats.overall.minimum,
        "max": stats.overall.maximum,
        "mean": f"{stats.overall.mean:.4f}",
    }
    for name, channel_stats in stats.per_channel.items():
        values[f"channel_{name}_min"] = channel_stats.minimum
        values[f"channel_{name}_max"] = channel_stats.maximum
        values[f"channel_{name}_mean"] = f"{channel_stats.mean:.4f}"
    return values


def run_operation(options: CliOptions) -> int:
    """Despacha a operação solicitada para o algoritmo correspondente."""

    # A infraestrutura anterior a esta função já cuidou da CLI, presença dos
    # arquivos e validação dos parâmetros gerais.
    #
    # TODO(aluno) M1.2: implementar brightness, contrast, negative, threshold
    # e histogram. result_io.py apenas serializa o vetor de 256 contadores;
    # a contagem dos pixels deve ser implementada pelo estudante.
    #
    # TODO(aluno) M1.3: implementar convolution, mean_filter, weighted_mean,
    # laplacian e sobel. kernel.py apenas lê e valida o kernel; aplicar a
    # convolução continua sendo responsabilidade do estudante.

    operation = options.operation
    image = read_image(options.input)

    if operation == "inspect":
        stats = inspect_image(image)
        _print_inspect(stats)
        if options.output:
            write_json_object(options.output, _inspect_as_dict(stats))
        return exit_code.SUCCESS

    if operation == "copy":
        write_image(options.output, copy_image(image))
        return exit_code.SUCCESS

    if operation in _CHANNEL_INDEX:
        write_image(options.output, extract_channel(image, _CHANNEL_INDEX[operation]))
        return exit_code.SUCCESS

    if operation == "grayscale_average":
        write_image(options.output, grayscale_average(image))
        return exit_code.SUCCESS

    if operation == "grayscale_weighted":
        write_image(options.output, grayscale_weighted(image))
        return exit_code.SUCCESS

    if operation == "quantize":
        levels = parameter_as_int(options, "levels")
        write_image(options.output, quantize_image(image, levels))
        return exit_code.SUCCESS

    print(
        f"Operacao '{options.operation}' reconhecida, "
        "mas ainda nao implementada no projeto-base.",
        file=sys.stderr,
    )
    return exit_code.GENERAL_ERROR
