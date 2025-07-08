## Riferimento Codice: ASM-ex1

`ASM-ex1` agisce come il produttore iniziale nella pipeline di dati.

### `main.py`

Punto di ingresso per l'applicazione `ASM-ex1`.

#### Funzione `run(enforcer, model_uploader, producer, topics)`
Esegue il ciclo di simulazione principale.
- **Argomenti**:
  - `enforcer (EnforcerExample)`: L'istanza dell'enforcer per comunicare con ASMeta-server.
  - `model_uploader (ModelUploader)`: L'istanza per caricare il modello ASM.
  - `producer (KafkaProducer)`: Il producer Kafka per inviare i messaggi.
  - `topics (list[str])`: La lista dei topic Kafka su cui pubblicare.
- **Logica**:
  1.  In un ciclo infinito, genera azioni predefinite (es. `FASTER`, `LANE_RIGHT`).
  2.  Chiama `enforcer.sanitise_output()` per validare l'azione.
  3.  Pubblica l'azione (originale o modificata) sui topic Kafka specificati.

### `enforcer.py`

Contiene la logica per interagire con il server ASMeta.

#### Classe `EnforcerExample`
Estende `RestClient` e gestisce il ciclo di vita dell'enforcement.
- **`__init__(self, ip, base_port, asm_name)`**: Inizializza il client REST e imposta il nome del modello ASM.
- **`begin_enforcement(self)`**: Avvia una nuova esecuzione del modello sul server ASMeta.
- **`end_enforcement(self)`**: Termina l'esecuzione del modello.
- **`sanitise_output(self, input_dict)`**: Invia l'azione e lo stato al server per la validazione e restituisce l'azione "enforced".
