from pathlib import Path
import pytest
import runpy
from hepscape.schema import load

ROOT = Path(__file__).resolve().parents[1]
convert = runpy.run_path(str(ROOT / 'scripts/importa_tabella_qid.py'))['convert']
SOURCE = ROOT / 'data/ern2026/lotti/roma_avezzano_online_originale.tsv'


def test_published_qid_lot_reproduces_all_answers():
    data = convert(SOURCE, 'Roma', 'Avezzano', 'Evento ERNEST - ERN 2026', 'ROMA-AVZ-ONLINE-ERN2026')
    assert data == load(ROOT / 'data/ern2026/lotti/roma_avezzano_online.json', True)
    assert len(data['records']) == 49
    assert data['records'][0]['answers']['Q7'] == 0
    assert data['records'][13]['answers']['Q1'] == 2
    assert data['records'][13]['answers']['Q9'] == 3
    assert data['records'][34]['answers']['Q2'] == 'INTERESSANTE \nDIVERTENTE \nEDUCATIVA'
    assert sum(r['answers']['Q2'] is None for r in data['records']) == 6


def test_unknown_option_and_wrong_location_are_rejected(tmp_path):
    changed = tmp_path / 'changed.tsv'
    changed.write_text(SOURCE.read_text().replace('Sì, un po’', 'non riconosciuta', 1))
    with pytest.raises(ValueError, match='opzione sconosciuta'):
        convert(changed, 'Roma', 'Avezzano', 'Test', 'TEST')
    with pytest.raises(ValueError, match='location'):
        convert(SOURCE, 'Roma', 'Terni', 'Test', 'TEST')
