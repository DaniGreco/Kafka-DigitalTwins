## Riferimento Codice: ASM-ex3

`ASM-ex3` agisce come un processore di stream intermedio, consumando dati da un topic, elaborandoli e pubblicandoli su un altro.

### `main.py`

Punto di ingresso per l'applicazione `ASM-ex3`.

- **Logica Principale**:
  1. Inizializza sia un `KafkaConsumer` che un `KafkaProducer`.
  2. Avvia un `consumer_thread` per ascoltare i messaggi in arrivo dal topic di input (quello di `ASM-ex1`).
  3. Quando un messaggio viene ricevuto, il thread chiama la funzione `run_simulation`.

#### Funzione `run_simulation(enforcer, model_uploader, producer, producer_topic, input_action)`
- **Argomenti**:
  - `enforcer (EnforcerExample)`: L'istanza dell'enforcer.
  - `model_uploader (ModelUploader)`: L'istanza per caricare il modello.
  - `producer (KafkaProducer)`: Il producer per inviare il risultato.
  - `producer_topic (str)`: Il topic di output.
  - `input_action (str)`: L'azione ricevuta dal consumer.
- **Logica**:
  1. Prende l'azione di input.
  2. La invia al server ASMeta tramite `enforcer.sanitise_output()` usando il modello ASM specifico di `ASM-ex3`.
  3. Pubblica l'azione risultante sul topic di output (`producer_topic`).

#### Funzione `consumer_thread(...)`
- **Logica**: Gestisce il ciclo di consumo dei messaggi e invoca `run_simulation` per ogni messaggio.
