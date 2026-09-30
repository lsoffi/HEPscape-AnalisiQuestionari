import pytest
from hepscape.comparison import wilson, difference_interval, tokens


def test_wilson_extremes_and_missing():
    assert wilson(0, 0) is None
    assert wilson(0, 10) == pytest.approx((0, 0.2775327998628892))
    assert wilson(10, 10) == pytest.approx((0.7224672001371107, 1))


def test_difference_symmetry_and_no_data():
    d, lo, hi = difference_interval(3, 10, 8, 20)
    dr, lr, hr = difference_interval(8, 20, 3, 10)
    assert d == pytest.approx(-0.1)
    assert (dr, lr, hr) == pytest.approx((-d, -hi, -lo))
    assert -1 <= lo < d < hi <= 1
    assert difference_interval(0, 0, 8, 20) is None


def test_zero_difference_retains_uncertainty():
    d, lo, hi = difference_interval(0, 10, 0, 10)
    assert d == 0
    assert lo < 0 < hi


def test_word_presence_and_editorial_exclusion():
    assert tokens("Bella BELLA e curiosità [incerto]") == {"BELLA", "CURIOSITÀ"}
