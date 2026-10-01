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
    assert tokens("Bella BELLA e curiosità [incerto]") == {"BELLO/BELLA", "CURIOSITÀ"}
    assert tokens("sono più ben mi tutto grazie ingressi interessante") == {"INTERESSANTE"}


def test_colors_follow_kit_identity():
    from hepscape.comparison import kit_colors

    assert kit_colors(["Pisa", "Roma", "Bari"]) == ["#5F8FC4", "#234A8C", "#7BBA48"]
    assert kit_colors(["Roma", "Perugia", "Bari", "Pisa"]) == [
        "#234A8C",
        "#39754B",
        "#7BBA48",
        "#5F8FC4",
    ]
    assert kit_colors(["Pisa", "Bari", "Perugia", "Roma"]) == list(
        reversed(kit_colors(["Roma", "Perugia", "Bari", "Pisa"]))
    )


def test_four_kit_wordwall_preserves_counts_and_colors(tmp_path):
    import csv
    from hepscape.comparison_wordwall import generate

    kits = ["Roma", "Perugia", "Bari", "Pisa"]
    texts = [
        ["INTERESSANTE COINVOLGENTE"],
        ["INTERESSANTE CURIOSA"],
        ["INTERESSANTE DIVERTENTE"],
        ["INTERESSANTE PUZZLE"],
    ]
    generate(texts, kits, tmp_path, "Test")
    with (tmp_path / "word_wall_insieme.csv").open(encoding="utf-8-sig") as f:
        words = {r["parola"]: r for r in csv.DictReader(f)}
    assert words["INTERESSANTE"]["totale"] == "4"
    assert words["CURIOSO/A"]["Perugia"] == "1"
    assert words["CURIOSO/A"]["Roma"] == "0"
    for kit in kits:
        assert float(words["INTERESSANTE"][f"quota_{kit}"]) == 0.25
    svg = (tmp_path / "12_word_wall_insieme.svg").read_text()
    assert "#39754B" in svg and "Pisa: 1 risposte" in svg


def test_three_kit_wordwall_preserves_exclusive_words(tmp_path):
    import csv
    from hepscape.comparison_wordwall import generate

    texts = [["INTERESSANTE IMMERSIVA"], ["INTERESSANTE CURIOSA"], ["INTERESSANTE PUZZLE"]]
    generate(texts, ["Roma", "Bari", "Pisa"], tmp_path, "Test")
    with (tmp_path / "word_wall_insieme.csv").open(encoding="utf-8-sig") as f:
        words = {r["parola"]: r for r in csv.DictReader(f)}
    assert set(words) == {"INTERESSANTE", "IMMERSIVO/A", "CURIOSO/A", "PUZZLE"}
    assert words["PUZZLE"]["Pisa"] == "1"
    assert words["PUZZLE"]["Roma"] == words["PUZZLE"]["Bari"] == "0"
    assert words["INTERESSANTE"]["totale"] == "3"
    assert float(words["INTERESSANTE"]["quota_Pisa"]) == pytest.approx(1 / 3)


def test_morphological_groups_count_once_per_answer():
    from hepscape.words import exact_tokens

    assert tokens("BELLA BELLO BELLE carina carino istruttiva istruttivo") == {
        "BELLO/BELLA",
        "CARINO/A",
        "ISTRUTTIVO/A",
    }
    assert exact_tokens("BELLA BELLO") == {"BELLA", "BELLO"}
    assert tokens("BELLA BELLISSIMA") == {"BELLO/BELLA", "BELLISSIMO/A"}
