# Usa un'immagine base con Python
FROM python:3.9-slim

# Imposta la directory di lavoro
WORKDIR /app

# Copia i file necessari
COPY producer.py .

# Installa le dipendenze
RUN pip install pyzmq kafka-python

# Esegui lo script
CMD ["python", "producer.py"]
