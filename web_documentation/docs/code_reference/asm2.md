## Riferimento Codice: ASM-ex2

`ASM-ex2` agisce come il consumatore finale nella pipeline di dati.

### `main.py`

Punto di ingresso per l'applicazione `ASM-ex2`.

- **Logica Principale**:
  1. Inizializza un `KafkaConsumer` per sottoscriversi ai topic specificati nel file `config.json`.
  2. Si mette in ascolto di nuovi messaggi.
  3. Per ogni messaggio ricevuto, decodifica il contenuto e lo stampa sulla console, mostrando l'azione finale elaborata dalla pipeline.
