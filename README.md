# HEPscape! · Analisi dei questionari

Dalle fotografie dei questionari all’Excel e ai grafici, con una revisione umana tracciabile.

Il repository include **109 questionari HEPscape! raccolti durante l’evento ERNEST – ERN 2026**, il workbook verificato e le tavole in palette HEPscape. Il lotto attuale ha `Città = Avezzano` e `Origine del kit = Roma`. Questi metadati restano nelle singole righe, così si possono aggiungere altri lotti e altre città. I risultati riguardano HEPscape!, non l’intero evento ERNEST.

## Risultati già pronti

- [Workbook verificato: 109 schede](data/ern2026/questionari.xlsx)
- [PDF originale preparato insieme: kit Roma, evento ad Avezzano](kits/roma/HEPscape_ERN2026_slide_originali.pdf)
- [Raccolta rigenerata dal programma, con grafici e word wall](reports/ern2026/HEPscape_raccolta_grafici.pdf)
- [Grafici PNG/SVG e tabelle CSV](reports/ern2026/grafici/)
- [Trascrizioni e codici verificati, in JSON](data/ern2026/questionari_verificati.json)
- [Storico delle trascrizioni e delle correzioni](data/ern2026/trascrizione_storica.json)

![Word wall Q2](reports/ern2026/grafici/12b_word_wall.png)

## Da dove cominciare

Un **workbook** è semplicemente un file Excel con più fogli. Gli **script** sono i programmi Python che eseguono la lettura delle foto, la creazione dell’Excel e l’analisi. Si avviano con i comandi riportati qui sotto; al momento non c’è un’interfaccia con pulsanti.

| Cosa vuoi fare? | Cosa serve? | Si usa l’API OpenAI? |
| --- | --- | --- |
| Consultare l’Excel, le slide e i grafici già pronti | Scaricare i file dai link sopra | No |
| Rigenerare grafici e word wall dai dati verificati | Installare il programma e seguire il punto 1 | No |
| Trascrivere nuovi questionari fotografati | Installare il lettore, configurare una chiave API e seguire il punto 2 | Sì, solo durante la lettura delle foto |
| Correggere le letture, creare l’Excel e unire altre città | Seguire i punti 3 e 4 | No |

Il percorso completo è **foto → bozza → controllo umano → Excel verificato → grafici e slide PDF**. Il programma propone le risposte; una persona le confronta con le fotografie prima di usarle nell’analisi.

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

## Guida pratica: come avviare i due script

Dopo l’installazione, apri il terminale nella cartella `HEPscape-AnalisiQuestionari` e attiva l’ambiente `.venv` come indicato sopra. Se hai già scaricato il repository, usa `git pull` da quella cartella per ricevere gli aggiornamenti. I comandi seguenti sono su una sola riga e si possono usare sia su macOS/Linux sia in PowerShell.

### A. Dalle foto al workbook Excel

Esempio: **kit Roma**, evento ad **Avezzano**, nuovo lotto `ROMA-AVZ-2026-02`.

1. Crea sul tuo computer la cartella `photos/roma/avezzano/` dentro il repository e mettici le nuove fotografie, una scheda per foto.
2. Configura `OPENAI_API_KEY` e `OPENAI_MODEL` seguendo [le istruzioni per la chiave API](#che-cosè-una-chiave-api).
3. Avvia la lettura delle foto:

```sh
hepscape extract photos/roma/avezzano --out work/roma-avezzano-02 --kit Roma --city Avezzano --prefix ROMA-AVZ-2026-02 --event "Evento ERNEST - ERN 2026" --send-to-openai
```

Questo primo comando **non fa domande interattive**: origine del kit e città dell’evento sono specificate con `--kit` e `--city`. Per un altro caso sostituisci questi valori, la cartella delle foto, il prefisso e la destinazione. Il prefisso deve essere unico per ogni lotto e la destinazione deve essere nuova o vuota.

4. Apri `work/roma-avezzano-02/bozza.xlsx` per vedere la proposta. Controlla anche `errori.json` per le foto escluse. Apri `revisione.csv` e confronta tutte le risposte con le foto: inserisci eventuali modifiche in `correzione` e scrivi `SI` in `confermato`. Per una risposta vuota confermata usa `__BLANK__`. Segui i dettagli del [punto 3](#3-risolvere-i-dubbi-e-confermare), mantenendo ID e colonna `controllo` come testo.
5. Dopo aver salvato il CSV revisionato, applica le conferme:

```sh
hepscape review work/roma-avezzano-02/bozza.json --apply work/roma-avezzano-02/revisione.csv --out work/roma-avezzano-02/verificati.json
```

6. Crea il workbook finale:

```sh
hepscape workbook work/roma-avezzano-02/verificati.json --out work/roma-avezzano-02/questionari.xlsx
```

Il risultato è **`work/roma-avezzano-02/questionari.xlsx`**. Se rimangono risposte non confermate, il programma chiede di completare la revisione prima di creare il file finale. La bozza viene generata automaticamente dalle foto; il controllo umano completa il passaggio all’Excel utilizzabile per l’analisi.

### B. Dal workbook ai grafici e al PDF

Per analizzare il workbook appena creato:

```sh
hepscape plots work/roma-avezzano-02/questionari.xlsx
```

Il programma chiede **quale kit analizzare**: Roma, Bari, Perugia, Pisa, Padova oppure **tutti**. Non richiede più la città dell’evento: per impostazione predefinita considera tutte le città e tutti gli eventi presenti nel workbook.

Per il kit Roma i risultati vanno in `kits/roma/tutte-le-citta/<data-e-ora>/`. Scegliendo tutti i kit vanno in `reports/tutti-i-kit/tutte-le-citta/<data-e-ora>/`. Il programma stampa il percorso completo al termine. Ogni esecuzione ha una cartella nuova.

La cartella contiene `HEPscape_raccolta_grafici.pdf`, grafici PNG/SVG, tabelle CSV, word wall, ZIP e `manifest.json`. Questa fase non richiede una chiave API. Il [PDF originale della prima analisi](kits/roma/HEPscape_ERN2026_slide_originali.pdf) resta in `kits/roma/`.

## 1. Analizzare un workbook unico con tutti gli eventi e i kit

Usa un solo workbook con una riga per questionario, ID univoci nell’intero file e le colonne Q1–Q11, **Città** (luogo dell’evento) e **Origine del kit**. Il lettore usa queste colonne per selezionare le schede. Non deduce l’evento dalla città: eventi diversi possono svolgersi nella stessa città.

Negli esempi `work/questionari_completi.xlsx` indica il tuo workbook unico: sostituiscilo con il percorso reale. Il file incluso `data/ern2026/questionari.xlsx` contiene solo il lotto iniziale di 109 questionari, kit Roma, evento ad Avezzano.

### Scegliere il kit con una domanda

```sh
hepscape plots work/questionari_completi.xlsx
```

Rispondi con il nome del kit oppure `tutti`. Il report di un kit include tutte le sue schede, anche raccolte in città ed eventi diversi. Il report di tutti i kit aggrega tutte le righe; ogni questionario pesa allo stesso modo, non ogni kit.

### Scegliere direttamente nel comando

```sh
hepscape plots work/questionari_completi.xlsx --kit Roma
hepscape plots work/questionari_completi.xlsx --kit tutti
```

La selezione non cambia l’Excel originale. Se non trova schede del kit richiesto, il programma segnala l’errore. Nel manifest sono registrati filtri e numero di schede analizzate.

### Aggiungere i confronti tra kit, quando servono

```sh
hepscape plots work/questionari_completi.xlsx --kit tutti --compare-kits
```

`--compare-kits` aggiunge tavole descrittive delle risposte a Q1, Q3, Q4 e Q5 per kit, con percentuali calcolate sulle risposte valide e numerosità dei gruppi. Servono almeno due kit presenti nei dati selezionati. Senza questa opzione il report aggregato non contiene queste tavole. Sono confronti descrittivi: differenze di pubblico, città o evento possono spiegare differenze tra kit; non misurano da sole l’efficacia del kit.

### Filtrare facoltativamente una città

```sh
hepscape plots work/questionari_completi.xlsx --kit Roma --city Avezzano
hepscape plots work/questionari_completi.xlsx --kit tutti --city Avezzano --compare-kits
```

Il filtro città include tutti gli eventi svolti lì. In questo caso la sottocartella è `avezzano` invece di `tutte-le-citta`. **Un filtro per singolo evento non è ancora previsto**: eventuali colonne aggiuntive sull’evento sono ignorate dall’analisi. Per ora il workbook unico viene aggregato per kit e, se richiesto, città.

### Scegliere destinazione e titolo

```sh
hepscape plots work/questionari_completi.xlsx --kit tutti --out work/report-completo --event "Raccolta HEPscape - tutti gli eventi"
```

`--event` imposta soltanto il titolo del report, non filtra le schede. Il titolo predefinito è “Tutti gli eventi”. `--out` sceglie una destinazione esplicita: riutilizzarla sovrascrive i file con lo stesso nome. Usando soltanto `--out`, senza selezione, si analizza l’intero workbook senza domande.

Per riprodurre il lotto storico:

```sh
hepscape plots data/ern2026/questionari.xlsx --kit Roma --event "Evento ERNEST - ERN 2026"
```

Per ricreare il workbook storico dai dati verificati:

```sh
hepscape workbook data/ern2026/questionari_verificati.json --out work/questionari.xlsx
```

Il file ricreato conserva codici, risposte, città e kit; lo stile è simile all’originale. Tutte le 109 righe vengono confrontate nei test.

## 2. Da nuove foto alla bozza Excel

Mettere le foto in una cartella, per esempio `photos/roma/`. Serve **una scheda intera per foto**, ben leggibile: JPG/JPEG, PNG o WEBP. Raddrizzare fogli molto inclinati ed evitare riflessi e parti tagliate. HEIC e PDF vanno prima convertiti. Per questionari con domande o opzioni diverse bisogna adattare lo schema: questo programma riconosce il modello italiano a 11 domande presente nei dati.

### Che cos’è una chiave API?

Un’**API** è un modo con cui un programma comunica con un servizio online. Qui lo script invia una foto a OpenAI e riceve una proposta di trascrizione delle risposte.

La **chiave API** è un codice segreto che autorizza queste richieste e le associa al tuo progetto OpenAI. È simile a una password per il programma: chi la possiede potrebbe utilizzare il servizio a carico del tuo account. Non è la password di ChatGPT e non va inserita nell’Excel, nel README o nei file pubblicati su GitHub. La [guida ufficiale OpenAI](https://developers.openai.com/api/docs/quickstart) spiega come crearla e renderla disponibile al programma.

### Come procurarsela e quanto costa

1. Accedi alla [piattaforma API OpenAI](https://platform.openai.com/), oppure crea un account.
2. Seleziona il progetto da usare e apri la sezione **API keys** per creare una chiave segreta. Se usi un progetto del tuo gruppo, chiedi al suo responsabile l’accesso previsto.
3. Verifica la fatturazione nella sezione **Billing** della piattaforma API. **L’uso dell’API viene fatturato separatamente dall’abbonamento ChatGPT**: avere un abbonamento ChatGPT non configura automaticamente la fatturazione dello script. Vedi la [spiegazione ufficiale sulla fatturazione](https://help.openai.com/en/articles/9039756-managing-billing-for-chatgpt-and-the-api-platform).
4. Conserva la chiave in un luogo privato. Rendila disponibile al programma sul tuo computer usando `OPENAI_API_KEY`, come nell’esempio sotto. Non inviarla in chat né condividerla nel repository.
5. Scegli un modello disponibile nel tuo account che supporti immagini e output strutturati, e indica il suo nome in `OPENAI_MODEL`.

Il software di questo repository non richiede un pagamento per l’uso. La **lettura delle nuove foto può generare costi OpenAI**, variabili in base al modello e alla quantità di dati elaborati. Consulta le [tariffe API aggiornate](https://developers.openai.com/api/docs/pricing) e controlla i consumi nella piattaforma. Non è indicato un prezzo fisso per questionario: fai prima una prova con poche foto e controlla il costo effettivo.

Se una chiave viene pubblicata per errore, revocala nella piattaforma e creane una nuova: eliminarla dal file non basta a renderla nuovamente segreta. Le [indicazioni ufficiali sulla gestione delle chiavi](https://developers.openai.com/api/docs/guides/production-best-practices) approfondiscono questo punto.

### Configurare la chiave ed eseguire la lettura

`OPENAI_API_KEY` e `OPENAI_MODEL` sono **variabili d’ambiente**, cioè impostazioni che il programma legge dal terminale. Sostituisci i testi di esempio tra virgolette con la tua chiave e il nome del modello. Le impostazioni mostrate valgono per la sessione corrente del terminale; se lo chiudi, dovrai impostarle di nuovo. La chiave resta privata sul tuo computer, ma viene usata per autenticare le richieste a OpenAI.

L’opzione `--send-to-openai` conferma esplicitamente l’invio delle foto selezionate. **Le foto lasciano quindi il computer durante questa fase.** Revisione, creazione dell’Excel, unione dei lotti e grafici funzionano invece in locale e non richiedono una chiave.

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

## 4. Unire lotti verificati dello stesso evento

```sh
hepscape merge data/ern2026/questionari_verificati.json work/roma-01/verificati.json --out work/tutte-le-citta.json
hepscape workbook work/tutte-le-citta.json --out work/tutte-le-citta.xlsx
hepscape plots work/tutte-le-citta.xlsx --out work/report-completo --event "Evento ERNEST - ERN 2026"
```

Questo comando `merge` unisce lotti dello stesso evento; non costruisce automaticamente un archivio di eventi diversi. L’analisi `plots` può invece leggere il workbook unico già predisposto con tutti gli eventi. L’unione preserva città, origine del kit, ID e provenienza. Rifiuta ID duplicati, foto con hash duplicato ed eventi discordanti. Gli ID del lotto storico sono `1`–`109`; i nuovi usano il prefisso scelto.

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

**Nella prima pubblicazione sono passati 17 test automatici**, sia in locale sia su GitHub con Python 3.10 e 3.12. Su GitHub è stata verificata anche la rigenerazione completa dei grafici dal workbook. Gli esiti delle esecuzioni successive sono consultabili nella [pagina dei test automatici](https://github.com/lsoffi/HEPscape-AnalisiQuestionari/actions).

Un test automatico controlla che il programma produca il risultato previsto per un caso preparato. I test coprono la corrispondenza di tutte le righe dell’Excel storico, codifiche, mancanti, revisione, duplicati, unioni, testo che sembra una formula, richiesta API simulata e analisi di un lotto senza risposte valide. GitHub Actions ripete i test senza chiavi o chiamate API.

**Il riconoscimento da foto non è stato validato con chiamate API reali in questa prima versione**, perché non era disponibile una chiave. La trascrizione dei 109 questionari è quella già verificata manualmente, non il risultato del nuovo estrattore. Nella prova simulata una risposta preparata sostituisce quella del servizio OpenAI: questo controlla il funzionamento del collegamento nel programma, senza inviare foto e senza costi API. Le prove simulate verificano il flusso software, non l’accuratezza della lettura. Il riconoscimento può sbagliare anche quando non segnala incertezza: controllare le schede prima dell’analisi. Variazioni di modello, versione e qualità delle foto possono cambiare le proposte.

Per la prima prova reale, usa poche foto e confronta ogni risposta proposta con il foglio: caselle selezionate, parole della Q2 e risposte vuote. Completa la revisione del punto 3 prima di generare l’Excel finale. Il superamento dei test software non garantisce che una crocetta o una parola manoscritta siano state lette correttamente.

## Dati e pubblicazione

Il repository pubblico contiene le risposte del lotto autorizzato e i risultati. Non contiene foto originali, chiavi API né percorsi personali del computer. Le cartelle `photos/` e `work/` sono escluse da Git per impostazione predefinita. L’estrazione invia soltanto le foto selezionate all’API OpenAI, ricodificate senza metadati EXIF, con `store=False`; ciò non equivale a garantire assenza di conservazione da parte del servizio. Applicare le condizioni del proprio account e verificare di poter trasmettere i nuovi questionari.

Prima di pubblicare nuovi lotti, controllare eventuali nomi o informazioni personali scritte nelle risposte libere e nelle note. La pubblicazione di questo lotto non autorizza automaticamente quella di altri lotti.

Il codice originale in `hepscape/` e `tests/` è distribuito con [licenza MIT](LICENSE). La licenza del codice non concede diritti aggiuntivi sui dati, sulle foto, sul marchio HEPscape! o sui contenuti dei siti citati.

Documentazione tecnica dell’API: [immagini](https://developers.openai.com/api/docs/guides/images-vision), [output strutturati](https://developers.openai.com/api/docs/guides/structured-outputs).
