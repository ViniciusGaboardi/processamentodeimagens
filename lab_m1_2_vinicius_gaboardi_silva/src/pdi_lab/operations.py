from __future__ import annotations

import sys

from . import exit_code
from .cli import CliOptions
from .image_io import read_image, write_image
from .intensity import (
    apply_brightness,
    apply_contrast,
    apply_negative,
    apply_threshold,
    compute_histogram,
)
from .parameters import parameter_as_float, parameter_as_int
from .result_io import write_histogram_csv


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


def run_operation(options: CliOptions) -> int:
    """Despacha a operação solicitada para sua implementação."""

    # A infraestrutura anterior a esta função já cuidou da CLI, presença dos
    # arquivos e validação dos parâmetros gerais.

    # M1.2 (transformações de intensidade) está implementado abaixo, com o
    # algoritmo de cada operação em `intensity.py` e percurso explícito dos
    # pixels, sem substituir a operação por uma função pronta equivalente do
    # OpenCV.

    # TODO(aluno) M1.1: implementar inspect, copy, channel_b, channel_g,
    # channel_r, grayscale_average, grayscale_weighted e quantize.

    # TODO(aluno) M1.3: implementar convolution, mean_filter, weighted_mean,
    # laplacian e sobel. kernel.py apenas lê e valida o kernel; aplicar a
    # convolução continua sendo responsabilidade do estudante.
    

    operation = options.operation

    if operation == "brightness":
        image = read_image(options.input)
        value = parameter_as_int(options, "value")
        write_image(options.output, apply_brightness(image, value))
        return exit_code.SUCCESS

    if operation == "contrast":
        image = read_image(options.input)
        alpha = parameter_as_float(options, "alpha")
        write_image(options.output, apply_contrast(image, alpha))
        return exit_code.SUCCESS

    if operation == "negative":
        image = read_image(options.input)
        write_image(options.output, apply_negative(image))
        return exit_code.SUCCESS

    if operation == "threshold":
        image = read_image(options.input)
        threshold = parameter_as_int(options, "threshold")
        write_image(options.output, apply_threshold(image, threshold))
        return exit_code.SUCCESS

    if operation == "histogram":
        image = read_image(options.input)
        write_histogram_csv(options.output, compute_histogram(image))
        return exit_code.SUCCESS

    print(
        f"Operacao '{options.operation}' reconhecida, "
        "mas ainda nao implementada no projeto-base.",
        file=sys.stderr,
    )
    return exit_code.GENERAL_ERROR
