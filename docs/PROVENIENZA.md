# Provenienza e riproducibilità

## Lotto iniziale

109 schede del questionario ERNEST relative all’attività HEPscape!, trascritte e verificate con le correzioni confermate dal titolare dei dati. Città: Avezzano; origine del kit: Roma. La denominazione generale delle figure è «HEPscape! · Evento ERNEST – ERN 2026».

- `data/ern2026/questionari.xlsx` è ora il workbook unico dei lotti Roma e Bari (207 schede); conserva risposte e codici delle 109 schede Roma.
- `data/ern2026/trascrizione_storica.json` conserva risposte, annotazioni e storia delle verifiche della sessione, con i percorsi personali ridotti ai soli nomi dei file.
- `data/ern2026/lotti/roma.json` conserva il lotto Roma nel formato del nuovo programma. I codici provengono dal workbook verificato; non da una nuova interpretazione delle foto.
- `kits/roma/HEPscape_ERN2026_slide_originali.pdf` è una copia della raccolta finale della sessione originale.
- `reports/ern2026/HEPscape_raccolta_grafici.pdf`, i PNG/SVG, i CSV, il word wall e il manifest sono rigenerati dal nuovo programma portabile.

La raccolta rigenerata usa gli stessi dati e criteri di quella originale. Nei pareggi delle frequenze lessicali usa un ordinamento alfabetico esplicito; non cambia i conteggi. Il confronto automatico dell’Excel ricreato verifica tutte le righe ID/Q1–Q11/città/kit. La grafica e i metadati interni dei file possono variare con le versioni delle librerie.

## Lotto Bari

98 schede lette visivamente in chat dalla scansione `hepscape_bari_survey1.pdf`, una scheda per pagina. Kit Bari, location Bari, stesso Evento ERNEST - ERN 2026, confermati dall’utente. Gli 11 dubbi A–K sono stati risolti esplicitamente dall’utente il 30 settembre 2026; le altre risposte sono state controllate visivamente in chat, senza conferma umana individuale. Il campo `reviewed` indica il completamento di questo controllo: la provenienza distingue il metodo, e `review_log` conserva le 11 decisioni dell’utente.

- `data/ern2026/lotti/bari.json`: 98 schede con pagina sorgente e storia delle correzioni.
- `data/ern2026/questionari_verificati.json`: unione dei due lotti (207 schede).
- `kits/bari/bari/ERN2026/`: report, grafici e tabelle filtrati sul kit Bari e location Bari.
- Le risposte vuote confermate D (pagina 39, Q2) e J (pagina 74, Q8) sono `null` nel JSON e 999 nell’Excel. L’annotazione «PIÙ O MENO» della pagina 74 resta nelle note.

La scansione e i ritagli usati per la revisione non sono pubblicati. I report preesistenti sotto `reports/ern2026/` restano riferiti alle sole 109 schede Roma.

## Nuove foto

Le foto vengono lette nella conversazione dell’utente, seguendo `docs/PROMPT_CHAT.md`. Il programma importa il CSV in locale e imposta tutte le risposte come da revisionare, anche se la chat le ha indicate come sicure. I JSON conservano il nome della foto, la trascrizione importata e la storia delle correzioni. L’importazione non calcola hash delle foto e non rileva automaticamente due scatti della stessa scheda: il controllo resta umano.

Il CSV non conserva tutte le conversazioni: archivia separatamente eventuali annotazioni e chiarimenti. La correttezza dei codici non garantisce l’accuratezza della lettura; confronta ogni scheda con la fotografia.

## Organizzazione del codice

- `schema.py`: domande, opzioni e validazione; unica fonte della codifica.
- `chat_import.py`: importazione locale del CSV ottenuto in chat.
- `review.py`: esportazione/applicazione delle correzioni con controllo della bozza di provenienza.
- `workbook.py`: esportazione Excel e lettura rigorosa dell’Excel per l’analisi.
- `plots.py`: tavole descrittive, conteggi e denominatori calcolati dal workbook.
- `wordwall.py`: disposizione deterministica delle parole per frequenza per scheda.
- `cli.py`: comandi `import-chat`, `review`, `workbook`, `merge`, `plots`.

I file di lavoro nuovi vanno in `work/`, le foto in `photos/`. Entrambe le cartelle sono escluse da Git. Per una nuova pubblicazione verificata, copiare intenzionalmente solo i dati e i risultati da condividere in una nuova sottocartella di `data/` e `reports/`.
