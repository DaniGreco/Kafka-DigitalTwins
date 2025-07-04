# Documentazione del Progetto: Kafka-DigitalTwins

## 1. Introduzione

Il progetto `Kafka-DigitalTwins` mira a stabilire un ambiente Kafka basato su Docker per simulare l'interazione tra un "Physical Twin" (simulazioni o sensori che generano dati) e un "Digital Twin" (modelli digitali che replicano il comportamento dei sistemi fisici). Il sistema utilizza Kafka come backbone per lo scambio di dati, con componenti dedicati per la produzione e il consumo di messaggi, e moduli "ASM-ex" che fungono da enforcer per i Digital Twin, interagendo con un server ASMeta.

L'obiettivo principale è implementare una pipeline dati che consenta:
- Trasmissione unidirezionale e bidirezionale di dati tra Physical Twin e Digital Twin.
- Registrazione accurata di ogni scambio di dati.
- Archiviazione dei dati raccolti per analisi successive.
- Integrazione di traduttori ZeroMQ-Kafka e REST-Kafka per garantire una comunicazione asincrona e scalabile.

## 2. Architettura Generale

Il sistema è composto dai seguenti macro-componenti, tutti containerizzati tramite Docker per garantire portabilità e isolamento:

-   **Kafka Cluster**: Un cluster Kafka con controller e broker per la gestione dei messaggi e dei topic.
-   **Producer**: Un'applicazione Python che funge da bridge tra ZeroMQ e Kafka, pubblicando i dati ricevuti via ZeroMQ su un topic Kafka.
-   **Consumer**: Un'applicazione Python che sottoscrive un topic Kafka e stampa i messaggi ricevuti.
-   **ASM-ex (Digital Twin Enforcer)**: Tre istanze separate (ASM-ex1, ASM-ex2, ASM-ex3) che rappresentano i Digital Twin. Questi moduli interagiscono con un server ASMeta per applicare logiche di enforcement e pubblicano azioni su Kafka.

-   **ASMeta Server**: Un server che esegue i modelli ASM (Abstract State Machine) a runtime, fornendo un'API REST per l'interazione con gli enforcer.

Il flusso di dati generale prevede che i "Physical Twin" (simulati o reali) inviino dati tramite ZeroMQ al `producer`. Il `producer` inoltra questi dati a Kafka. I moduli `ASM-ex` (Digital Twin) leggono i dati, li elaborano tramite il server ASMeta per l'enforcement, e possono pubblicare azioni corrette o nuove su Kafka, che possono poi essere consumate da altri sistemi o dal `consumer` per il logging.

## 3. Dettagli dei Componenti

### 3.1. Kafka Cluster (`docker-compose.yml`)

Il file `docker-compose.yml` definisce un cluster Kafka robusto, composto da:
-   **Tre Controller Kafka (`controller-1`, `controller-2`, `controller-3`)**: Gestiscono la ridondanza e la resilienza dei metadati del cluster. Utilizzano `confluentinc/cp-kafka` e sono configurati con `KAFKA_PROCESS_ROLES: controller`.
-   **Un Broker Kafka (`broker`)**: Responsabile della gestione dei topic e dello smistamento dei dati. È configurato con `KAFKA_PROCESS_ROLES: broker` e dipende dai controller. Espone la porta `9092`.
-   **Kafka Setup (`kafka-setup`)**: Un servizio one-shot che attende che il broker sia pronto e poi crea i topic Kafka necessari (`asm1-output`, `asm3-output`). Questo assicura che i topic siano disponibili prima che producer e consumer tentino di connettersi.

Tutti i servizi Kafka sono interconnessi tramite la rete Docker `kafka-network`.

### 3.2. Producer (`producer/producer.py`)

Il `producer.py` è un'applicazione Python che funge da bridge tra un'interfaccia ZeroMQ e Kafka.
-   **Funzionalità**: Si connette a un server ZeroMQ (attualmente configurato per `tcp://host.docker.internal:5555`) e sottoscrive tutti i messaggi. Ogni messaggio ricevuto via ZeroMQ viene immediatamente pubblicato sul topic Kafka `'my-topic'`.
-   **Logging**: Implementa un logging di base che scrive i messaggi inviati a Kafka nel file `producer/logs/app.log`.
-   **Containerizzazione**: Viene costruito da un `Dockerfile` nella directory `producer/` e aggiunto al `docker-compose.yml` come servizio `producer`.

### 3.3. Consumer (`consumer/consumer.py`)

Il `consumer.py` è un'applicazione Python semplice che consuma messaggi da Kafka.
-   **Funzionalità**: Si connette al broker Kafka (`broker:9092`) e sottoscrive il topic `'my-topic'`. Ogni messaggio ricevuto viene decodificato e stampato sulla console.
-   **Containerizzazione**: Viene costruito da un `Dockerfile` nella directory `consumer/` e aggiunto al `docker-compose.yml` come servizio `consumer`.

### 3.4. ASM-ex (Digital Twin Enforcer) (`ASM-ex1/main.py`, `ASM-ex1/enforcer.py`)

Le directory `ASM-ex1`, `ASM-ex2`, `ASM-ex3` contengono implementazioni di "Digital Twin Enforcer" basati su modelli ASM. Sebbene siano replicati, la logica principale è contenuta in `ASM-ex1`.

-   **`main.py`**:
    -   Punto di ingresso per l'applicazione ASM-ex.
    -   Configura il logging e inizializza un `KafkaProducer` per inviare messaggi.
    -   Inizializza un `EnforcerExample` e un `ModelUploader` per interagire con il server ASMeta.
    -   La funzione `run` simula una serie di azioni (`FASTER`, `LANE_RIGHT`, `SLOWER`, `LANE_LEFT`, `IDLE`) e le invia al server ASMeta tramite l'enforcer per la "sanitizzazione" (applicazione della logica di enforcement).
    -   L'azione (originale o modificata dall'enforcer) viene poi inviata a un topic Kafka (es. `asm1-output` per `asm1`).
    -   Gestisce l'upload e la cancellazione del modello ASM a runtime sul server ASMeta.
-   **`enforcer.py`**:
    -   Contiene la classe `EnforcerExample` che estende `RestClient` (presumibilmente da `reusable-modules/rest_client.py` in `external/ASMeta`).
    -   **`begin_enforcement()`**: Avvia una nuova esecuzione del modello ASM sul server ASMeta.
    -   **`end_enforcement()`**: Ferma l'esecuzione del modello ASM.
    -   **`sanitise_output(input_dict)`**: Questo è il cuore della logica di enforcement. Prende un dizionario di input (rappresentante le variabili monitorate dal sistema), lo invia al server ASMeta per un "step" di simulazione, e riceve un'azione "enforced" (sanitizzata). Se l'azione enforced è diversa dall'input originale, significa che l'enforcer è intervenuto.
-   **Containerizzazione**: Ogni istanza ASM-ex (es. `asm1`) viene costruita dal proprio `Dockerfile` e configurata nel `docker-compose.yml`. Dipendono dal `kafka-setup` (per la creazione dei topic) e dall'`asmeta-server`.

### 3.5. ASMeta Server (`external/ASMeta/asmeta_server/Dockerfile`)

Il servizio `asmeta-server` è un'applicazione Java (probabilmente un JAR eseguibile) che funge da runtime per i modelli ASM.
-   **Funzionalità**: Espone un'API REST (sulla porta `8080`) che consente ai moduli ASM-ex di caricare, avviare, eseguire step e fermare i modelli ASM.
-   **Containerizzazione**: Viene costruito da un `Dockerfile` nella directory `external/ASMeta/asmeta_server/` e aggiunto al `docker-compose.yml`.

## 4. Flusso di Dati

1.  **Generazione Dati (Physical Twin)**: Un sistema esterno (simulato o reale) genera dati e li pubblica tramite ZeroMQ.
2.  **Ingresso Kafka (Producer)**: Il `producer.py` ascolta i messaggi ZeroMQ, li riceve e li pubblica sul topic Kafka `'my-topic'`.
3.  **Consumo Dati (Consumer)**: Il `consumer.py` legge i messaggi da `'my-topic'` e li stampa, fungendo da semplice monitor.
4.  **Elaborazione Digital Twin (ASM-ex)**:
    *   I moduli `ASM-ex` (es. `asm1`) generano azioni simulate (es. `FASTER`, `LANE_RIGHT`, `SLOWER`, `LANE_LEFT`, `IDLE`).
    *   Queste azioni, insieme ad altre variabili di stato (es. `rightLaneFree`), vengono inviate all'`asmeta-server` tramite l'`EnforcerExample` per la "sanitizzazione" (applicazione della logica di enforcement).
    *   L'`asmeta-server` esegue uno step del modello ASM e restituisce un'azione "enforced" (potenzialmente modificata).
    *   L'azione (originale o enforced) viene poi pubblicata su un topic Kafka specifico per l'ASM (es. `asm1-output`).

## 5. Prerequisiti

Per eseguire il progetto, è necessario avere installato:
-   **Docker**: Per la containerizzazione di tutti i servizi.

## 6. Guida Rapida (Quickstart)

1.  Assicurati di avere Docker installato e in esecuzione.
2.  Naviga nella directory principale del progetto `Kafka-DigitalTwins`.
3.  Esegui il seguente comando per avviare tutti i servizi:
    ```bash
    docker-compose up --build
    ```
    Potrebbe essere necessario attendere alcuni minuti affinché tutti i container si avviino correttamente, in particolare il cluster Kafka. Se i container `consumer` e `producer` non si avviano automaticamente, potrebbe essere necessario avviarli manualmente tramite i comandi Docker.

## 7. Struttura del Progetto

```
Kafka-DigitalTwins/
├── .git/
├── .gitignore
├── .gitmodules
├── docker-compose.yml             # Definizione dei servizi Docker
├── README.md                      # Panoramica del progetto e guida rapida
├── ASM-ex1/                       # Modulo Digital Twin Enforcer (es. Pillbox)
│   ├── client-proxy.py
│   ├── config.json                # Configurazione per ASM-ex1
│   ├── configuration_manager.py
│   ├── Dockerfile                 # Dockerfile per ASM-ex1
│   ├── enforcer.py                # Logica di enforcement del Digital Twin
│   ├── entrypoint.sh
│   ├── logging_manager.py
│   ├── main.py                    # Punto di ingresso per ASM-ex1
│   ├── model_uploader.py
│   ├── requirements.txt
│   ├── rest_client.py
│   ├── log/
│   └── resources/                 # Risorse del modello ASM
│       ├── libraries/
│       └── models/
├── ASM-ex2/                       # Replica di ASM-ex1
├── ASM-ex3/                       # Replica di ASM-ex1
├── consumer/                      # Applicazione Consumer Kafka
│   ├── consumer.py                # Logica del consumer
│   └── Dockerfile
├── docs/                          # Documentazione del progetto
│   ├── Requisiti software per Kafka e data streams per Digital Twins.pdf
│   └── Requisiti software per Kafka e data streams per Digital Twins/
│       └── Requisiti software per Kafka e data streams per Digital Twins.md # Documento requisiti
├── external/                      # Moduli esterni (ASMeta, breathe)
│   ├── ASMeta/                    # Server ASMeta e moduli riutilizzabili
│   │   ├── asmeta_server/         # Implementazione del server ASMeta
│   │   │   ├── asmeta_runtime_server.py
│   │   │   ├── AsmetaServer.jar
│   │   │   └── Dockerfile
│   │   └── reusable-modules/      # Moduli Python riutilizzabili
│   └── breathe/                   # Progetto Breathe (simulatore medico)
└── producer/                      # Applicazione Producer Kafka
    ├── Dockerfile
    ├── producer.py                # Logica del producer (ZeroMQ to Kafka)
    └── logs/
```

## 8. Lavoro Futuro (To-Do)

Basandosi sul `README.md` e sull'analisi del codice, i seguenti punti sono identificati come aree di miglioramento o lavoro futuro:

-   **Schema per la gestione dei dati**: Definire uno schema strutturato per i messaggi Kafka per una gestione più efficiente.
-   **Risoluzione `docker-compose.yml`**: Il `README.md` indica che il file `docker-compose.yml` potrebbe necessitare di correzioni o miglioramenti per un avvio più affidabile.
-   **Implementazione completa dei Physical Twin**: Attualmente, il `producer` si connette a un server ZeroMQ generico. L'integrazione con simulatori specifici (come quelli menzionati nella documentazione `docs/`) dovrebbe essere chiarita o implementata.
-   **Gestione degli errori e resilienza**: Migliorare la gestione degli errori e la resilienza dei componenti Kafka e ASM-ex.
-   **Test**: Aggiungere test unitari e di integrazione per i vari componenti.
