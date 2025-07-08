# Documentazione: Pipeline di Elaborazione Dati con Kafka e ASMeta

## 1. Introduzione

Questo progetto implementa una pipeline di elaborazione dati multi-stadio che utilizza **Apache Kafka** come sistema di messaggistica e un **ASMeta Server** per la validazione e la correzione della logica di business. La pipeline simula un flusso di lavoro in cui un'azione viene generata, processata attraverso molteplici "enforcer" (garanti della logica), e infine consumata.

Il sistema è composto da tre moduli principali, `ASM-ex1`, `ASM-ex3`, e `ASM-ex2`, che agiscono in sequenza:
-   **`ASM-ex1`**: Agisce come **produttore iniziale**. Genera un'azione, la valida tramite il server ASMeta e la pubblica su un topic Kafka.
-   **`ASM-ex3`**: Agisce come **processore di stream intermedio**. Consuma i messaggi da `ASM-ex1`, applica la *propria* logica di validazione tramite il server ASMeta e pubblica il risultato su un nuovo topic Kafka.
-   **`ASM-ex2`**: Agisce come **consumatore finale**. Si sottoscrive al topic di `ASM-ex3` e riceve il dato finale elaborato.

L'intera architettura è containerizzata tramite Docker, garantendo portabilità e coerenza dell'ambiente.

## 2. Architettura e Flusso dei Dati

Il flusso dei dati è sequenziale e attraversa tre fasi distinte, orchestrate da Kafka.

**Fase 1: Generazione e Prima Validazione (`ASM-ex1`)**
1.  `ASM-ex1/main.py` genera un'azione (es. `"FASTER"`).
2.  L'azione viene inviata al server ASMeta tramite il modulo `enforcer.py` per una prima validazione basata sul modello ASM caricato da `ASM-ex1`.
3.  Il server ASMeta restituisce un'azione "sanitizzata" (corretta o confermata).
4.  `ASM-ex1` pubblica l'azione finale su un topic Kafka (es. `asm1-output`).

**Fase 2: Elaborazione Intermedia e Seconda Validazione (`ASM-ex3`)**
1.  `ASM-ex3/main.py` consuma il messaggio dal topic `asm1-output`.
2.  L'azione ricevuta viene inviata nuovamente al server ASMeta, ma questa volta `ASM-ex3` utilizza il *proprio* modello ASM per una seconda, diversa validazione.
3.  Il server ASMeta restituisce un'azione "sanitizzata" secondo la logica di `ASM-ex3`.
4.  `ASM-ex3` pubblica l'azione finale su un secondo topic Kafka (es. `asm3-output`).

**Fase 3: Consumo Finale (`ASM-ex2`)**
1.  `ASM-ex2/main.py` consuma il messaggio finale dal topic `asm3-output`.
2.  Il messaggio viene registrato o stampato, concludendo la pipeline.

Questo flusso può essere visualizzato come segue:
`ASM-ex1` -> `Kafka (topic: asm1-output)` -> `ASM-ex3` -> `Kafka (topic: asm3-output)` -> `ASM-ex2`

## 3. Dettagli dei Componenti

### 3.1. ASM-ex1 (Produttore Iniziale)
-   **Logica Principale (`main.py`)**: In un ciclo, genera azioni predefinite, le passa all'`enforcer` per la validazione e utilizza un `KafkaProducer` per inviarle al topic di output.
-   **Configurazione (`config.json`)**: Specifica l'indirizzo del server ASMeta, il percorso del modello ASM da usare e il topic Kafka su cui pubblicare.

### 3.2. ASM-ex3 (Processore di Stream)
-   **Logica Principale (`main.py`)**: Utilizza un `KafkaConsumer` per ricevere messaggi in un thread dedicato. Per ogni messaggio, invoca la logica di validazione tramite l'`enforcer` e usa un `KafkaProducer` per inoltrare il risultato al topic di output.
-   **Configurazione (`config.json`)**: Specifica il topic di input (`consumer_topic`) e quello di output (`producer_topic`), oltre ai dettagli del server ASMeta e del modello ASM specifico per questa fase.

### 3.3. ASM-ex2 (Consumatore Finale)
-   **Logica Principale (`main.py`)**: Implementa unicamente un `KafkaConsumer` che si mette in ascolto sul topic di output di `ASM-ex3`. Ogni messaggio ricevuto viene stampato a console.
-   **Configurazione (`config.json`)**: Specifica i topic da cui consumare i messaggi.

### 3.4. Enforcer (`enforcer.py`)
Questo modulo è un componente riutilizzabile presente in ogni `ASM-ex`.
-   **Funzionalità**: Incapsula la logica di comunicazione con il server ASMeta. Il metodo `sanitise_output` invia lo stato corrente e l'azione proposta al server tramite una richiesta HTTP `PUT` e restituisce la risposta del server.

### 3.5. ASMeta Server
-   **Funzionalità**: È un servizio Java che espone un'API REST. Permette di caricare modelli ASM, avviare sessioni di esecuzione e processare "step" di simulazione, applicando la logica definita nel modello caricato.

### 3.6. Kafka Cluster (`docker-compose.yml`)
-   **Setup**: Il file `docker-compose.yml` definisce i servizi per l'intero sistema, inclusi i controller e i broker Kafka, e un servizio `kafka-setup` che crea i topic necessari (`asm1-output`, `asm3-output`) all'avvio.

## 4. Guida all'Avvio

1.  Assicurarsi che Docker sia installato e in esecuzione.
2.  Dalla directory principale del progetto, eseguire il comando:
    ```bash
    docker-compose up --build
    ```
3.  Questo comando costruirà le immagini Docker per ogni componente e avvierà i container. Il sistema inizierà automaticamente a eseguire il flusso di dati descritto.

## 5. Struttura del Progetto
```
Kafka-DigitalTwins/
├── docker-compose.yml             # Definizione dei servizi Docker
├── ASM-ex1/                       # Produttore iniziale
│   ├── main.py
│   ├── enforcer.py
│   ├── config.json
│   └── Dockerfile
├── ASM-ex2/                       # Consumatore finale
│   ├── main.py
│   ├── enforcer.py
│   ├── config.json
│   └── Dockerfile
├── ASM-ex3/                       # Processore di stream intermedio
│   ├── main.py
│   ├── enforcer.py
│   ├── config.json
│   └── Dockerfile
├── external/
│   └── ASMeta/
│       └── asmeta_server/         # Server ASMeta
└── web_documentation/
    └── docs/
        └── index.md               # Questa documentazione
```