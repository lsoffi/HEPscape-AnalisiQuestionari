# HEPscape! · Analisi dei questionari

Dalle fotografie dei questionari all’Excel e ai grafici, con una revisione umana tracciabile.

Il repository include **109 questionari HEPscape! raccolti durante l’evento ERNEST – ERN 2026**, il workbook verificato e le tavole in palette HEPscape. Il lotto attuale ha `Città = Avezzano` e `Origine del kit = Roma`. Questi metadati restano nelle singole righe, così si possono aggiungere altri lotti e altre città. I risultati riguardano HEPscape!, non l’intero evento ERNEST.

## Risultati già pronti

- [Workbook verificato: 109 schede](data/ern2026/questionari.xlsx)
- [Slide con tutti i grafici e il word wall](reports/ern2026/HEPscape_raccolta_grafici.pdf)
- [Grafici PNG/SVG e tabelle CSV](reports/ern2026/grafici/)
- [Trascrizioni e codici verificati, in JSON](data/ern2026/questionari_verificati.json)
- [Storico delle trascrizioni e delle correzioni](data/ern2026/trascrizione_storica.json)

![Word wall Q2](reports/ern2026/grafici/12b_word_wall.png)

## Installazione

Serve **Python 3.10 o successivo**. I comandi seguenti vanno eseguiti nel terminale, dalla cartella del repository.

```sh
git clone https://github.com/lsoffi/HEPscape-AnalisiQuestionari.git
cd HEPscape-AnalisiQuestionari
python -m venv .venv
```

Attivare l’ambiente:

```sh
# macOS / Linux
source .venv/bin/activate
# Windows PowerShell (in alternativa al comando sopra)
.venv\Scripts\Activate.ps1
```

Installare il programma, incluso il lettore di foto:

```sh
python -m pip install -e ".[vision]"
hepscape --help
```

Per usare solo Excel e grafici, senza il lettore di immagini, basta `python -m pip install -e .`.
Le versioni usate nella verifica iniziale sono riportate in [docs/versioni-verificate.txt](docs/versioni-verificate.txt); i requisiti ammettono anche versioni compatibili.

## 1. Riprodurre i risultati già presenti, senza API

```sh
hepscape plots data/ern2026/questionari.xlsx --out work/report \
  --event "Evento ERNEST - ERN 2026"
```

Produce grafici PNG e SVG, tabelle CSV, word wall, metodo, raccolta PDF e ZIP. Il word wall segue la tavola 12. Tutti i denominatori sono calcolati dal workbook: non sono fissati a 109. Se sono presenti più città o kit, si aggiungono i confronti per queste variabili.

Per ricreare anche il workbook dai dati verificati:

```sh
hepscape workbook data/ern2026/questionari_verificati.json --out work/questionari.xlsx
hepscape plots work/questionari.xlsx --out work/report-ricreato
```

Il file ricreato conserva codici, risposte originali, città e kit del workbook iniziale; lo stile è simile, non una copia identica del file binario. Tutte le 109 righe vengono confrontate automaticamente nei test.

## 2. Da nuove foto alla bozza Excel

Mettere le foto in una cartella, per esempio `photos/roma/`. Serve **una scheda intera per foto**, ben leggibile: JPG/JPEG, PNG o WEBP. Raddrizzare fogli molto inclinati ed evitare riflessi e parti tagliate. HEIC e PDF vanno prima convertiti. Per questionari con domande o opzioni diverse bisogna adattare lo schema: questo programma riconosce il modello italiano a 11 domande presente nei dati.

Il lettore usa l’API OpenAI. Serve una propria chiave, un modello abilitato a leggere immagini e produrre output strutturati, e credito API. L’invio è esplicito; Excel, revisione, unione e grafici funzionano completamente in locale. Non serve una chiave per riprodurre i dati di esempio.

```sh
# macOS / Linux: impostare nel proprio ambiente; non salvare la chiave nel repository
export OPENAI_API_KEY="la-propria-chiave"
export OPENAI_MODEL="nome-del-modello-disponibile"

hepscape extract photos/roma --out work/roma-01 \
  --city "Roma" --kit "Roma" --prefix "ROMA-2026-01" \
  --event "Evento ERNEST - ERN 2026" --send-to-openai
```

In PowerShell le variabili si impostano con `$env:OPENAI_API_KEY="..."` e `$env:OPENAI_MODEL="..."`. I comandi possono essere scritti su un’unica riga. Il modello è configurabile anche con `--model`: non è imposto un modello che potrebbe non essere disponibile nell’account.

Si possono indicare anche singoli file, separati da spazi:

```sh
hepscape extract foto1.jpg foto2.jpg --out work/lotto-02 --city "Roma" --kit "Roma" --prefix "ROMA-2026-02" --send-to-openai
```

Il prefisso deve essere diverso per ogni lotto. La numerazione deriva dall’ordine dei file (alfabetico per una cartella), non dal numero scritto sul foglio; quest’ultimo viene conservato come informazione da verificare.

La cartella di output deve essere nuova o vuota. Il risultato contiene:

| File | Uso |
| --- | --- |
| `bozza.xlsx` | Prima lettura in Excel; non ancora ammessa all’analisi |
| `bozza.json` | Risposte proposte, testo originale, dubbi, metadati e hash delle foto |
| `revisione.csv` | File da aprire in Excel per correggere e confermare |
| `letture/` | Output strutturato del modello per ciascuna foto |
| `errori.json` | Foto non lette, non riconosciute o duplicate |

Le foto identiche byte per byte vengono escluse; due scatti diversi della stessa scheda richiedono ancora un controllo umano. Gli errori non fermano il salvataggio delle schede già lette: il comando restituisce un codice di uscita diverso da zero e segnala il numero di foto escluse. **Controllare sempre `errori.json` e riconciliare il numero delle schede con quello atteso.** Per riprovare foto fallite usare un nuovo lotto e un nuovo prefisso, poi unire i risultati verificati.

## 3. Risolvere i dubbi e confermare

Aprire `revisione.csv` in Excel come CSV UTF-8, delimitatore virgola, mantenendo **ID e colonna `controllo` come testo**. Ogni riga corrisponde a una domanda di una scheda. Confrontarla con la foto originale.

- `proposta` e `motivo` mostrano la lettura del modello. **Non modificare `proposta`: non è il campo di correzione.**
- In `correzione` inserire il codice corretto; per Q2 il testo corretto. Lasciare vuoto per conservare la proposta.
- Per dichiarare una risposta effettivamente vuota scrivere **`__BLANK__`** in `correzione`. In Excel diventerà 999.
- Scrivere **`SI`** in `confermato` dopo aver controllato la risposta. Vanno verificate anche quelle che il modello considera chiare.
- Non eliminare righe e non cambiare `id`, `domanda` o `controllo`. Un controllo automatico impedisce di applicare una revisione a una bozza diversa.

Una lettura illeggibile o dubbia **non viene convertita automaticamente in 999**. In bozza è indicata come `DA VERIFICARE`. Se manca anche una proposta, occorre inserire esplicitamente una correzione oppure `__BLANK__`.

Salvare il CSV e applicarlo:

```sh
hepscape review work/roma-01/bozza.json --apply work/roma-01/revisione.csv --out work/roma-01/verificati.json
hepscape workbook work/roma-01/verificati.json --out work/roma-01/questionari.xlsx
hepscape plots work/roma-01/questionari.xlsx --out work/roma-01/report
```

L’Excel finale viene creato solo quando tutte le risposte sono confermate. Per riprendere una revisione parziale, riesportare il CSV dal JSON aggiornato:

```sh
hepscape review work/roma-01/verificati.json --export work/roma-01/revisione-successiva.csv
```

## 4. Aggiungere altre città

```sh
hepscape merge data/ern2026/questionari_verificati.json work/roma-01/verificati.json --out work/tutte-le-citta.json
hepscape workbook work/tutte-le-citta.json --out work/tutte-le-citta.xlsx
hepscape plots work/tutte-le-citta.xlsx --out work/report-completo --event "Evento ERNEST - ERN 2026"
```

L’unione preserva città, origine del kit, ID e provenienza. Rifiuta ID duplicati, foto con hash duplicato ed eventi discordanti. Gli ID del lotto storico sono `1`–`109`; i nuovi usano il prefisso scelto.

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

## Verifica e limiti

```sh
python -m pip install -e ".[vision,test]"
python -m pytest -q
```

I test coprono la corrispondenza di tutte le righe dell’Excel storico, codifiche, mancanti, revisione, duplicati, unioni, testo che sembra una formula, richiesta API simulata e analisi di un lotto senza risposte valide. GitHub Actions ripete i test senza chiavi o chiamate API.

**Il riconoscimento da foto non è stato validato con chiamate API reali in questa prima versione**, perché non era disponibile una chiave. La trascrizione dei 109 questionari è quella già verificata manualmente, non il risultato del nuovo estrattore. Le prove simulate verificano il flusso software, non l’accuratezza della lettura. Il riconoscimento può sbagliare anche quando non segnala incertezza: controllare le schede prima dell’analisi. Variazioni di modello, versione e qualità delle foto possono cambiare le proposte.

## Dati e pubblicazione

Il repository pubblico contiene le risposte del lotto autorizzato e i risultati. Non contiene foto originali, chiavi API né percorsi personali del computer. Le cartelle `photos/` e `work/` sono escluse da Git per impostazione predefinita. L’estrazione invia soltanto le foto selezionate all’API OpenAI, ricodificate senza metadati EXIF, con `store=False`; ciò non equivale a garantire assenza di conservazione da parte del servizio. Applicare le condizioni del proprio account e verificare di poter trasmettere i nuovi questionari.

Prima di pubblicare nuovi lotti, controllare eventuali nomi o informazioni personali scritte nelle risposte libere e nelle note. La pubblicazione di questo lotto non autorizza automaticamente quella di altri lotti.

Il codice originale in `hepscape/` e `tests/` è distribuito con [licenza MIT](LICENSE). La licenza del codice non concede diritti aggiuntivi sui dati, sulle foto, sul marchio HEPscape! o sui contenuti dei siti citati.

Documentazione tecnica dell’API: [immagini](https://developers.openai.com/api/docs/guides/images-vision), [output strutturati](https://developers.openai.com/api/docs/guides/structured-outputs).
