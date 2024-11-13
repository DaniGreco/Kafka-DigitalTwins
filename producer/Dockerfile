FROM python:3.9
RUN pip install kafka-python
COPY producer.py /app/producer.py
WORKDIR /app
CMD ["python", "-u", "producer.py"]
