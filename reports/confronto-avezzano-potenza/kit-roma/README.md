# Avezzano e Potenza — solo kit Roma

[Report PDF](HEPscape_Avezzano_Potenza_kit_Roma.pdf), con grafici PNG/SVG, distribuzioni complete, confronto per età e parole Q2.

## Campioni

- Avezzano, ERN2026: **158** schede, di cui 109 cartacee e 49 online.
- Potenza, Lucania is comics: **113** schede da fotografie, aggiornate il 22 ottobre 2026. Il nuovo lotto aggiunge 32 schede: sono escluse due informative, una seconda foto della scheda 86 e la scheda 85 su istruzione dell’utente. [Dettaglio e inventario](../../../data/LIC2026/README.md).
- Filtro esplicito su città e kit Roma in entrambi i workbook. ID univoci verificati.

## Risultati principali

Percentuali sulle risposte valide alla singola domanda, esclusi i mancanti 999. Differenza = Potenza meno Avezzano, in punti percentuali.

| Risposta | Avezzano | Potenza | Differenza |
| --- | ---: | ---: | ---: |
| Gradimento: tantissimo | 58,2% (92/158) | 51,8% (58/112) | −6,4 |
| Apprendimento: sì, molto | 60,6% (94/155) | 51,8% (58/112) | −8,9 |
| Più curiosità | 66,5% (103/155) | 73,5% (83/113) | +7,0 |
| Più interesse | 65,6% (103/157) | 72,3% (81/112) | +6,7 |
| Facilità: sì, molto | 75,6% (118/156) | 69,6% (78/112) | −6,0 |

Il gradimento complessivamente positivo («tantissimo» o «mi è piaciuta») è 98,7% ad Avezzano e 98,2% a Potenza (110/112), sulle risposte valide. La differenza riguarda soprattutto l’intensità del gradimento.

Il pubblico differisce: i 15–18 anni sono il 38,5% ad Avezzano e il 15,9% a Potenza; i 26–60 anni il 28,8% e il 53,1%. Il confronto per età mostra differenze non uniformi e diversi sottogruppi piccoli. Evento, pubblico e modalità di raccolta non sono controllati: questi dati non stabiliscono quale città o attività sia più efficace.

## Riproduzione

Dalla radice del repository:

```sh
python scripts/confronta_avezzano_potenza.py
```

`risposte.csv` contiene conteggi, validi, mancanti e percentuali di tutte le domande chiuse. `per_eta.csv` contiene Q1/Q3/Q4/Q5 per fascia di età. `manifest.json` registra fonti, impronte SHA256, ID selezionati e indicatori principali. Le parole seguono gli accorpamenti già definiti in `hepscape/words.py`, contando ciascuna parola una volta per risposta.
