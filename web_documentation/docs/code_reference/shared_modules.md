## Riferimento Codice: Moduli Condivisi

Questi moduli forniscono funzionalità riutilizzabili per tutti i componenti `ASM-ex`.

### `configuration_manager.py`

#### Classe `ConfigurationManager`
Gestisce il caricamento della configurazione da un file `config.json`.
- **`__init__(self, config_file)`**: Carica il file JSON.
- **`get_server_params(self)`**: Restituisce i parametri di connessione per il server ASMeta (IP, porta, path del modello).
- **`get_kafka_params(self)`**: Restituisce i parametri per la connessione a Kafka (bootstrap servers, topics).
- **`get_logging_params(self)`**: Restituisce i parametri per il logging.

### `rest_client.py`

#### Classe `RestClient`
Fornisce un client HTTP di base per comunicare con l'API REST del server ASMeta.
- **`__init__(self, ip, base_port)`**: Inizializza l'URL di base dell'API.
- **`_resolve_api_endpoint(self, ip)`**: Determina dinamicamente l'indirizzo IP del server, con supporto per ambienti WSL.
- **`_send_request(self, method, endpoint, **kwargs)`**: Invia una richiesta HTTP generica al server, gestendo errori e timeout.

### `model_uploader.py`

#### Classe `ModelUploader`
Estende `RestClient` e gestisce l'upload e la rimozione dei modelli ASM sul server.
- **`__init__(self, ip, base_port, asm_base_path, asm_name)`**: Inizializza i percorsi dei file del modello e delle librerie.
- **`upload_runtime_model(self)`**: Carica il file del modello ASM e le sue librerie (es. `StandardLibrary.asm`) sul server.
- **`delete_runtime_model(self)`**: Rimuove il modello e le librerie dal server.
