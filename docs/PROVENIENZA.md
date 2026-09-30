# Provenienza e riproducibilità

## Lotto iniziale

109 schede del questionario ERNEST relative all’attività HEPscape!, trascritte e verificate con le correzioni confermate dal titolare dei dati. Città: Avezzano; origine del kit: Roma. La denominazione generale delle figure è «HEPscape! · Evento ERNEST – ERN 2026».

- `data/ern2026/questionari.xlsx` è il workbook finale della sessione originale, copiato senza modificare celle o formattazione.
- `data/ern2026/trascrizione_storica.json` conserva risposte, annotazioni e storia delle verifiche della sessione, con i percorsi personali ridotti ai soli nomi dei file.
- `data/ern2026/questionari_verificati.json` usa il formato del nuovo programma. I codici provengono dal workbook verificato; non da una nuova interpretazione delle foto.
- `reports/ern2026/slides.pdf` è una copia della raccolta finale della sessione originale.
- `reports/ern2026/HEPscape_raccolta_grafici.pdf`, i PNG/SVG, i CSV, il word wall e il manifest sono rigenerati dal nuovo programma portabile.

La raccolta rigenerata usa gli stessi dati e criteri di quella originale. Nei pareggi delle frequenze lessicali usa un ordinamento alfabetico esplicito; non cambia i conteggi. Il confronto automatico dell’Excel ricreato verifica tutte le righe ID/Q1–Q11/città/kit. La grafica e i metadati interni dei file possono variare con le versioni delle librerie.

## Nuove foto

La lettura automatica è una proposta da rivedere, non una misura dell’accuratezza. I file JSON conservano modello dichiarato, nome della foto, hash SHA-256, testo letto, note, stato della lettura e correzioni. Nessuna risposta viene inferita in base ad altre risposte. Tutte le letture devono essere confermate prima di esportare l’Excel finale.

Le prove API della prima versione sono simulate: verificano il formato della richiesta e la gestione di risposte incomplete o duplicate. Non sostituiscono una prova su foto reali con un modello e una chiave API. I 109 questionari inclusi non sono un risultato del nuovo estrattore.

Per valutare il riconoscimento, scegliere un campione di foto, trascriverlo manualmente in modo indipendente e confrontare ogni domanda con le proposte, distinguendo errori su caselle, mancanti e testo libero. Non considerare la sola validità del JSON una prova della correttezza della lettura.

## Organizzazione del codice

- `schema.py`: domande, opzioni e validazione; unica fonte della codifica.
- `photos.py`: invio immagini e interpretazione dello schema strutturato.
- `review.py`: esportazione/applicazione delle correzioni con controllo della bozza di provenienza.
- `workbook.py`: esportazione Excel e lettura rigorosa dell’Excel per l’analisi.
- `plots.py`: tavole descrittive, conteggi e denominatori calcolati dal workbook.
- `wordwall.py`: disposizione deterministica delle parole per frequenza per scheda.
- `cli.py`: comandi `extract`, `review`, `workbook`, `merge`, `plots`.

I file di lavoro nuovi vanno in `work/`, le foto in `photos/`. Entrambe le cartelle sono escluse da Git. Per una nuova pubblicazione verificata, copiare intenzionalmente solo i dati e i risultati da condividere in una nuova sottocartella di `data/` e `reports/`.
