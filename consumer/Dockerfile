FROM python:3.9
RUN pip install kafka-python
COPY consumer.py /app/consumer.py
WORKDIR /app
CMD ["python", "-u", "consumer.py"]
