import numpy as np
import pytest

from pdi_lab.errors import PdiError
from pdi_lab.image_io import read_image
from pdi_lab.intensity import (
    apply_brightness,
    apply_contrast,
    apply_negative,
    apply_threshold,
    compute_histogram,
)

# images/input/m1_gray_5x5.png contem uma rampa 10..250 (passo 10), conforme
# images/reference/small_images_reference.json. Os valores abaixo foram
# calculados manualmente a partir dessa rampa para conferir a implementacao.
GRAY_5X5_PATH = "images/input/m1_gray_5x5.png"


@pytest.fixture(scope="module")
def gray_5x5() -> np.ndarray:
    return read_image(GRAY_5X5_PATH)


def test_reference_pixels_match_expected_ramp(gray_5x5: np.ndarray):
    assert gray_5x5.shape == (5, 5)
    assert gray_5x5[0].tolist() == [10, 20, 30, 40, 50]
    assert gray_5x5[4].tolist() == [210, 220, 230, 240, 250]


def test_brightness_positive_and_negative_saturate(gray_5x5: np.ndarray):
    brighter = apply_brightness(gray_5x5, 30)
    assert brighter[0].tolist() == [40, 50, 60, 70, 80]
    # 230+30=260 e 240+30=270 e 250+30=280 devem saturar em 255.
    assert brighter[4].tolist() == [240, 250, 255, 255, 255]

    darker = apply_brightness(gray_5x5, -30)
    # 10-30=-20 e 20-30=-10 devem saturar em 0.
    assert darker[0].tolist() == [0, 0, 0, 10, 20]
    assert darker[4].tolist() == [180, 190, 200, 210, 220]


def test_contrast_identity_at_alpha_one(gray_5x5: np.ndarray):
    result = apply_contrast(gray_5x5, 1.0)
    assert result.tolist() == gray_5x5.tolist()


def test_contrast_reduced_at_alpha_half(gray_5x5: np.ndarray):
    result = apply_contrast(gray_5x5, 0.5)
    # g = 0.5*(f-128)+128 = 0.5f + 64
    assert result[0].tolist() == [69, 74, 79, 84, 89]
    assert result[4].tolist() == [169, 174, 179, 184, 189]


def test_contrast_expanded_at_alpha_one_and_half_saturates(gray_5x5: np.ndarray):
    result = apply_contrast(gray_5x5, 1.5)
    # g = 1.5*(f-128)+128 = 1.5f - 64; extremos devem saturar em 0 e 255.
    assert result[0].tolist() == [0, 0, 0, 0, 11]
    assert result[4].tolist() == [251, 255, 255, 255, 255]


def test_negative(gray_5x5: np.ndarray):
    result = apply_negative(gray_5x5)
    assert result[0].tolist() == [245, 235, 225, 215, 205]
    assert result[4].tolist() == [45, 35, 25, 15, 5]


def test_threshold_two_values(gray_5x5: np.ndarray):
    low = apply_threshold(gray_5x5, 100)
    assert low[0].tolist() == [0, 0, 0, 0, 0]
    assert low[1].tolist() == [0, 0, 0, 0, 255]

    high = apply_threshold(gray_5x5, 200)
    assert high[2].tolist() == [0, 0, 0, 0, 0]
    assert high[3].tolist() == [0, 0, 0, 0, 255]
    assert high[4].tolist() == [255, 255, 255, 255, 255]


def test_histogram_of_synthetic_image_has_one_pixel_per_intensity(gray_5x5: np.ndarray):
    histogram = compute_histogram(gray_5x5)
    assert len(histogram) == 256
    assert sum(histogram) == 25
    for value in range(10, 251, 10):
        assert histogram[value] == 1
    assert histogram[0] == 0
    assert histogram[255] == 0


def test_histogram_shifts_with_brightness(gray_5x5: np.ndarray):
    original = compute_histogram(gray_5x5)
    shifted = compute_histogram(apply_brightness(gray_5x5, 30))

    assert sum(original) == sum(shifted) == 25
    # Os tres maiores valores (230, 240, 250) saturam em 255 apos +30,
    # entao passam a se acumular na mesma posicao do histograma.
    assert shifted[255] == 3
    assert shifted[40] == 1
    assert shifted[0] == 0


def test_color_image_is_rejected_for_intensity_operations():
    color_image = read_image("images/input/m1_color_2x2.png")
    with pytest.raises(PdiError):
        apply_negative(color_image)
