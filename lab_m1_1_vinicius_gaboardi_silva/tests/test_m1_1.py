from pathlib import Path

import cv2
import numpy as np
import pytest

from pdi_lab import exit_code
from pdi_lab.__main__ import main
from pdi_lab.errors import PdiError
from pdi_lab.m1_1 import (
    copy_image,
    extract_channel,
    grayscale_average,
    grayscale_weighted,
    inspect_image,
    quantize_image,
)

# Pixels de images/input/m1_color_2x2.png, na ordem BGR usada pelo OpenCV
# (ver images/reference/small_images_reference.json para a versao RGB).
COLOR_2X2_BGR = np.array(
    [
        [[0, 0, 255], [0, 255, 0]],
        [[255, 0, 0], [255, 255, 255]],
    ],
    dtype=np.uint8,
)

# Matriz de images/input/m1_gray_5x5.png (ver images/reference/m1_gray_5x5.csv).
GRAY_5X5 = np.array(
    [
        [10, 20, 30, 40, 50],
        [60, 70, 80, 90, 100],
        [110, 120, 130, 140, 150],
        [160, 170, 180, 190, 200],
        [210, 220, 230, 240, 250],
    ],
    dtype=np.uint8,
)


def test_copy_is_pixel_exact():
    copied = copy_image(COLOR_2X2_BGR)
    assert copied is not COLOR_2X2_BGR
    assert np.array_equal(copied, COLOR_2X2_BGR)

    copied_gray = copy_image(GRAY_5X5)
    assert np.array_equal(copied_gray, GRAY_5X5)


def test_extract_channel_preserves_only_the_requested_channel():
    blue_only = extract_channel(COLOR_2X2_BGR, 0)
    green_only = extract_channel(COLOR_2X2_BGR, 1)
    red_only = extract_channel(COLOR_2X2_BGR, 2)

    assert np.array_equal(blue_only[:, :, 0], COLOR_2X2_BGR[:, :, 0])
    assert np.array_equal(blue_only[:, :, 1], np.zeros((2, 2), dtype=np.uint8))
    assert np.array_equal(blue_only[:, :, 2], np.zeros((2, 2), dtype=np.uint8))

    assert np.array_equal(green_only[:, :, 1], COLOR_2X2_BGR[:, :, 1])
    assert np.array_equal(red_only[:, :, 2], COLOR_2X2_BGR[:, :, 2])


def test_extract_channel_rejects_non_bgr_input():
    with pytest.raises(PdiError):
        extract_channel(GRAY_5X5, 0)


def test_grayscale_average_matches_manual_formula():
    result = grayscale_average(COLOR_2X2_BGR)
    # (R+G+B)/3 para vermelho, verde, azul e branco puros.
    expected = np.array([[85, 85], [85, 255]], dtype=np.uint8)
    assert np.array_equal(result, expected)


def test_grayscale_weighted_matches_manual_formula():
    result = grayscale_weighted(COLOR_2X2_BGR)
    # 0.299R + 0.587G + 0.114B arredondado, para R,G,B puros e branco.
    expected = np.array([[76, 150], [29, 255]], dtype=np.uint8)
    assert np.array_equal(result, expected)


def test_grayscale_average_and_weighted_differ_on_saturated_channels():
    average = grayscale_average(COLOR_2X2_BGR)
    weighted = grayscale_weighted(COLOR_2X2_BGR)
    assert not np.array_equal(average, weighted)


@pytest.mark.parametrize(
    "levels,expected_unique_values",
    [
        (2, {0, 128}),
        (4, {0, 64, 128, 192}),
        (8, {0, 32, 64, 96, 128, 160, 192, 224}),
        (16, {0, 16, 32, 48, 64, 80, 96, 112, 128, 144, 160, 176, 192, 208, 224, 240}),
    ],
)
def test_quantize_produces_at_most_the_requested_levels(levels, expected_unique_values):
    result = quantize_image(GRAY_5X5, levels)
    unique_values = set(int(v) for v in np.unique(result))
    assert unique_values.issubset(expected_unique_values)
    assert result.min() >= 0
    assert result.max() <= 255


def test_quantize_two_levels_matches_manual_calculation():
    result = quantize_image(GRAY_5X5, 2)
    expected = np.array(
        [
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 128, 128, 128],
            [128, 128, 128, 128, 128],
            [128, 128, 128, 128, 128],
        ],
        dtype=np.uint8,
    )
    assert np.array_equal(result, expected)


def test_quantize_keeps_boundary_values_in_range():
    boundary = np.array([[0, 255]], dtype=np.uint8)
    for levels in (2, 4, 8, 16):
        result = quantize_image(boundary, levels)
        assert result[0, 0] == 0
        assert 0 <= int(result[0, 1]) <= 255


def test_quantize_rejects_invalid_levels():
    with pytest.raises(PdiError):
        quantize_image(GRAY_5X5, 3)


def test_inspect_reports_dimensions_and_overall_stats():
    stats = inspect_image(GRAY_5X5)
    assert stats.width == 5
    assert stats.height == 5
    assert stats.channels == 1
    assert stats.pixel_count == 25
    assert stats.overall.minimum == 10
    assert stats.overall.maximum == 250
    assert stats.overall.mean == pytest.approx(130.0)
    assert stats.per_channel == {}


def test_inspect_reports_per_channel_stats_for_color_images():
    stats = inspect_image(COLOR_2X2_BGR)
    assert stats.channels == 3
    assert set(stats.per_channel) == {"b", "g", "r"}
    assert stats.per_channel["r"].maximum == 255
    assert stats.per_channel["b"].minimum == 0


def test_cli_inspect_prints_expected_keys(capsys):
    code = main(
        [
            "--operation",
            "inspect",
            "--input",
            "images/input/m1_gray_5x5.png",
        ]
    )
    assert code == exit_code.SUCCESS
    output = capsys.readouterr().out
    assert "width=5" in output
    assert "height=5" in output
    assert "channels=1" in output
    assert "pixels=25" in output
    assert "min=10" in output
    assert "max=250" in output


def test_cli_quantize_writes_output_file(tmp_path: Path):
    output = tmp_path / "quant.png"
    code = main(
        [
            "--operation",
            "quantize",
            "--input",
            "images/input/m1_gray_5x5.png",
            "--output",
            str(output),
            "--levels",
            "4",
        ]
    )
    assert code == exit_code.SUCCESS
    assert output.exists()

    written = cv2.imread(str(output), cv2.IMREAD_UNCHANGED)
    assert set(int(v) for v in np.unique(written)).issubset({0, 64, 128, 192})


def test_cli_channel_r_writes_three_channel_image(tmp_path: Path):
    output = tmp_path / "channel_r.png"
    code = main(
        [
            "--operation",
            "channel_r",
            "--input",
            "images/input/m1_color_2x2.png",
            "--output",
            str(output),
        ]
    )
    assert code == exit_code.SUCCESS

    written = cv2.imread(str(output), cv2.IMREAD_UNCHANGED)
    assert written.shape == (2, 2, 3)
    assert np.array_equal(written[:, :, 2], COLOR_2X2_BGR[:, :, 2])
    assert np.array_equal(written[:, :, 0], np.zeros((2, 2), dtype=np.uint8))
    assert np.array_equal(written[:, :, 1], np.zeros((2, 2), dtype=np.uint8))
