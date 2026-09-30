# HEPscape! · Analisi dei questionari

**Foto in chat → trascrizione CSV → revisione → workbook Excel → grafici e PDF.**

Le fotografie si caricano nella propria conversazione con ChatGPT, come abbiamo fatto per il primo lotto. Questo repository importa la trascrizione e svolge le elaborazioni sul computer: **non richiede una chiave API, non chiama OpenAI e non legge autonomamente le fotografie**. L’uso della chat segue le funzionalità e i limiti del proprio account; il repository non fornisce accesso alla chat.

## Risultati già pronti

Il lotto iniziale contiene 109 questionari HEPscape! dell’evento ERNEST – ERN 2026, raccolti ad Avezzano con kit Roma.

- [Workbook verificato](data/ern2026/questionari.xlsx)
- [Report Roma / Avezzano con copertina](kits/roma/avezzano/ERN2026/HEPscape_raccolta_grafici.pdf)
- [PDF originale preparato insieme, nella cartella Roma](kits/roma/HEPscape_ERN2026_slide_originali.pdf)
- [Grafici e word wall rigenerati](reports/ern2026/HEPscape_raccolta_grafici.pdf)
- [PNG, SVG e tabelle](reports/ern2026/grafici/)
- [Dati verificati e riutilizzabili](data/ern2026/questionari_verificati.json)

## Installazione

Serve Python 3.10 o successivo. Apri il terminale ed esegui:

```sh
git clone https://github.com/lsoffi/HEPscape-AnalisiQuestionari.git
cd HEPscape-AnalisiQuestionari
python -m venv .venv
```

Attiva l’ambiente su macOS/Linux:

```sh
source .venv/bin/activate
```

Oppure su Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Installa il programma:

```sh
python -m pip install -e .
hepscape --help
```

Se hai già il repository, esegui `git pull` e ripeti l’installazione nell’ambiente attivato. La versione corrente sostituisce il vecchio comando `extract`: non servono più `OPENAI_API_KEY`, `OPENAI_MODEL` o il componente `vision`.

## 1. Leggere le fotografie nella chat

1. Apri una conversazione con ChatGPT e allega fotografie leggibili, una scheda intera per foto. Puoi procedere in più lotti.
2. Copia il testo di [istruzioni per la trascrizione in chat](docs/PROMPT_CHAT.md), indicando città dell’evento, origine del kit e un prefisso univoco per gli ID.
3. Chiedi di elencare i dubbi e risolvili confrontando le foto. Controlla anche le risposte proposte come sicure e il numero totale delle schede.
4. Chiedi il file **`trascrizione.csv`**, scaricalo e salvalo in `work/trascrizione.csv` dentro il repository, creando prima la cartella `work/`.

Non basta rinominare un file Excel in CSV. Se la chat restituisce soltanto testo CSV, copialo in un file di testo UTF-8 senza le delimitazioni del blocco di codice. Il [modello CSV](examples/trascrizione_modello.csv) contiene solo l’intestazione corretta, senza dati fittizi da confondere con risposte reali.

Le colonne obbligatorie sono `ID,Foto,Q1,Q2,Q3,Q4,Q5,Q6,Q7,Q8,Q9,Q10,Q11`. Il separatore è la virgola; testi che contengono virgole devono essere racchiusi tra virgolette. I codici sono nella legenda sotto. `999` significa risposta vuota; `DA_VERIFICARE` significa lettura incerta. Un campo CSV lasciato vuoto viene trattato come incerto. Ogni ID deve essere unico.

## 2. Dalla trascrizione al workbook

Esempio: kit Roma, evento ad Avezzano. Avvia questo comando su una sola riga:

```sh
hepscape import-chat work/trascrizione.csv --out work/roma-avezzano-02 --kit Roma --city Avezzano --event "Evento ERNEST - ERN 2026"
```

Sostituisci città, kit, evento e percorsi per il tuo lotto. Il CSV deve contenere un solo lotto con questi metadati comuni; importa separatamente lotti di città, kit o eventi diversi. La destinazione deve essere nuova o vuota. L’importazione è interamente locale.

Il programma crea:

| File | Scopo |
| --- | --- |
| `bozza.xlsx` | Proposta di workbook da consultare |
| `bozza.json` | Dati di lavoro per i passaggi successivi |
| `revisione.csv` | Risposte da confermare o correggere |

Apri `revisione.csv` in Excel come CSV UTF-8, delimitatore virgola, mantenendo **ID e colonna `controllo` come testo**. Per ogni risposta:

- Confronta `proposta` con la foto; non modificare direttamente questa colonna.
- Metti il valore corretto in `correzione`, oppure lascia vuoto per mantenere la proposta.
- Per una risposta effettivamente vuota scrivi `__BLANK__` in `correzione`.
- Scrivi `SI` in `confermato` dopo aver controllato. Anche le risposte già chiarite in chat vanno confermate qui.
- Non eliminare righe né cambiare ID, domanda o colonna `controllo`.

Una risposta incerta senza proposta richiede un valore oppure `__BLANK__`; non viene trasformata automaticamente in 999. Salva il CSV e applica la revisione:

```sh
hepscape review work/roma-avezzano-02/bozza.json --apply work/roma-avezzano-02/revisione.csv --out work/roma-avezzano-02/verificati.json
hepscape workbook work/roma-avezzano-02/verificati.json --out work/roma-avezzano-02/questionari.xlsx
```

Il secondo comando crea l’Excel finale solo quando tutte le risposte sono confermate. Per proseguire una revisione parziale, riesporta il CSV aggiornato:

```sh
hepscape review work/roma-avezzano-02/verificati.json --export work/roma-avezzano-02/revisione-successiva.csv
```

## 3. Dal workbook all’analisi

Il programma può analizzare un **workbook unico con tutti gli eventi e tutti i kit**. Ogni scheda deve avere un ID unico e le colonne Q1–Q11, Città e Origine del kit. Le risposte vuote devono essere codificate come 999.

Per analizzare il nuovo workbook:

```sh
hepscape plots work/roma-avezzano-02/questionari.xlsx
```

Il programma chiede prima quale kit analizzare: **Roma, Bari, Perugia, Pisa, Padova oppure tutti**. Poi elenca le location presenti per quel kit, lette dalla colonna **Città**, e chiede di scegliere una location oppure **0 per tutti i dati del kit**. Non occorre ricordare o riscrivere il nome della location. Salva in `kits/roma/tutte-le-citta/<data-e-ora>/` per Roma, oppure in `reports/tutti-i-kit/tutte-le-citta/<data-e-ora>/` per tutti. Ogni esecuzione guidata ha una nuova cartella.

Negli esempi seguenti sostituisci `work/questionari_completi.xlsx` con il tuo workbook unico:

```sh
hepscape plots work/questionari_completi.xlsx --kit Roma --all-locations
hepscape plots work/questionari_completi.xlsx --kit tutti --all-locations
hepscape plots work/questionari_completi.xlsx --kit tutti --all-locations --compare-kits
```

`--compare-kits` aggiunge confronti descrittivi per Q1, Q3, Q4 e Q5 quando sono presenti almeno due kit. Senza questa opzione il report aggregato non contiene confronti tra kit. Ogni questionario pesa allo stesso modo; i kit non ricevono automaticamente lo stesso peso.

Per limitare l’analisi a una città:

```sh
hepscape plots work/questionari_completi.xlsx --kit Roma --city Avezzano
```

Puoi usare anche `--location Avezzano`, equivalente a `--city Avezzano`. L’output va sotto `kits/roma/avezzano/<data-e-ora>/`; per un evento di kit Bari va sotto `kits/bari/<location>/<data-e-ora>/`, e così per gli altri kit. Con `--all-locations` analizzi tutto il kit senza la domanda sulla location. In esecuzioni non interattive, omettere il filtro location include tutte le location. Il filtro include tutti gli eventi svolti in quella città; non esiste ancora un filtro per singolo evento. Eventuali colonne aggiuntive sull’evento vengono ignorate dall’analisi. `--event` cambia soltanto il titolo del report:

```sh
hepscape plots data/ern2026/questionari.xlsx --kit Roma --event "Evento ERNEST - ERN 2026"
```

Questo comando permette di provare subito il lotto storico, senza foto né chat. Il titolo predefinito è “Raccolta HEPscape”. Puoi aggiungere `--out work/report` per una destinazione esplicita; riutilizzarla sovrascrive i file con lo stesso nome. Con il solo `--out`, senza filtri, viene analizzato tutto il workbook senza domande.

Il **PDF inizia con una copertina con il logo ufficiale HEPscape!** che riporta il nome del kit, la location dell’evento e il numero di questionari selezionati. Per l’aggregato riporta “Tutte le location”; se scegli tutti i kit riporta “Tutti i kit”. Le pagine successive contengono i plot e il metodo. La copertina sposta di una pagina la numerazione precedente delle tavole.

L’output contiene PDF, PNG/SVG, tabelle CSV, word wall, ZIP e `manifest.json` con selezione e numero di schede. I confronti tra città sono aggiunti quando ne sono presenti più di una. I risultati sono descrittivi: le differenze possono dipendere dal pubblico e dagli eventi, non solo dal kit.

## 4. Unire lotti verificati dello stesso evento

```sh
hepscape merge data/ern2026/questionari_verificati.json work/roma-avezzano-02/verificati.json --out work/uniti.json
hepscape workbook work/uniti.json --out work/questionari_completi.xlsx
```

`merge` richiede lo stesso nome evento e ID univoci. Non costruisce automaticamente un archivio di eventi diversi: `plots` può invece analizzare il workbook unico già predisposto. Conserva i JSON verificati per mantenere la provenienza dei lotti.

## Codifica

| Domanda | Codici |
| --- | --- |
| Q1 | 0 tantissimo; 1 piaciuta; 2 non molto |
| Q2 | Testo in MAIUSCOLO nell’Excel codificato; originale conservato separatamente |
| Q3 | 0 sì molto; 1 sì un po’; 2 no |
| Q4 | 0 più curioso/a; 1 come prima; 2 meno curioso/a |
| Q5 | 0 più interessato/a; 1 come prima; 2 meno interessato/a |
| Q6 | 0 sì molto; 1 in parte; 2 no |
| Q7 | 0 spesso; 1 a volte; 2 mai |
| Q8 | 1 sì; 0 no |
| Q9 | 0 femminile; 1 maschile; 2 altro; 3 preferisco non rispondere |
| Q10 | 0 meno di 11; 1 11–14; 2 15–18; 3 19–25; 4 26–40; 5 41–60; 6 più di 60; 7 preferisco non rispondere |
| Q11 | 1 sì; 0 no |
| Tutte | 999 = risposta vuota confermata, inclusa Q2 |

Nel JSON i mancanti sono `null`; solo nell’Excel diventano 999. “Preferisco non rispondere” rimane una categoria esplicita, distinta da una casella vuota. Ogni colonna Excel riporta in alto il testo della domanda e la legenda.

## Cosa significano i grafici

Analisi descrittiva, senza test di significatività né inferenze causali. I codici sono categorie, non punteggi da mediare. I 999 sono esclusi dal denominatore valido; nei confronti servono entrambe le risposte. I gruppi con meno di 10 risposte sono contrassegnati con un asterisco.

Per Q2 si conta **in quante schede compare una parola**: “BELLA BELLA” conta una volta. Si escludono parole funzionali e annotazioni editoriali tra parentesi quadre. Il word wall include tutte le forme esatte rimanenti; la dimensione del carattere cresce con la radice quadrata della frequenza. Non è una proporzione esatta dell’area occupata dalla parola. La tavola delle forme accorpate è separata e documenta gli accorpamenti; i refusi non vengono corretti nelle forme esatte.

La palette deriva dal [sito HEPscape!](https://web.infn.it/hepscape/): `#234A8C`, `#335BA6`, `#5F8FC4`, `#7BBA48`, con `#18304F` per testi e contrasto. Non vengono assegnati colori di sentiment alle parole.

## Verifiche e limiti

```sh
python -m pip install -e ".[test]"
python -m pytest -q
```

I test controllano codifiche, importazione CSV, risposte incerte, revisione, duplicati, corrispondenza con le 109 schede storiche e analisi per uno o tutti i kit. [GitHub Actions](https://github.com/lsoffi/HEPscape-AnalisiQuestionari/actions) ripete i controlli e rigenera i grafici. Queste prove non misurano l’accuratezza della lettura delle fotografie in chat: verifica sempre le trascrizioni, anche quando non sono segnalati dubbi.

## Dati e pubblicazione

I programmi del repository lavorano in locale e non inviano foto o trascrizioni a servizi esterni. Quando alleghi foto in chat, le condividi con il servizio di chat secondo le condizioni del tuo account. Non sono caricate automaticamente su GitHub.

Il repository contiene il lotto storico autorizzato, senza fotografie originali. `photos/` e `work/` sono escluse da Git; i report sotto `kits/` e `reports/` non vengono pubblicati automaticamente: la pubblicazione richiede un caricamento esplicito. Prima di condividere nuovi lotti controlla eventuali nomi o informazioni personali nelle risposte libere.

Il codice originale è distribuito con [licenza MIT](LICENSE). La licenza del codice non concede diritti aggiuntivi sui dati, sulle foto o sul marchio HEPscape!. La [provenienza](docs/PROVENIENZA.md) descrive il lotto iniziale.
