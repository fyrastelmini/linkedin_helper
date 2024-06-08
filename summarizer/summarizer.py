import torch
from transformers import pipeline
from flask import Flask, request, jsonify, make_response
from bs4 import BeautifulSoup
import requests
from kafka import KafkaConsumer,KafkaProducer
from kafka.errors import NoBrokersAvailable
import json
import os
import time

summarizer = pipeline(
    "summarization",
    "pszemraj/long-t5-tglobal-base-16384-book-summary",
    device=0 if torch.cuda.is_available() else -1,
)
def create_producer():
    while True:
        try:
            producer = KafkaProducer(bootstrap_servers='kafka:9092',
                                     value_serializer=lambda v: json.dumps(v).encode('utf-8'))
            return producer
        except NoBrokersAvailable:
            print("Broker not available, retrying...")
            time.sleep(3)


def summarize(text: str) -> str:
    long_text = "Summerize the key requirements for applying to this Job offer: "+text
    return summarizer(long_text)[0]["summary_text"]

app = Flask(__name__)

def extract_div_content(data, div_class):
    if True:
        soup = BeautifulSoup(data, "html.parser")
        target_div = soup.find("div", {"class": div_class})

        if target_div:
            data = target_div.text.strip()
                
            return make_response(jsonify({
                "data": data
            }),200)
        else:
            return make_response(jsonify({"error": f"Div with class '{div_class}' not found on the page."}),404)


def create_consumer():
    while True:
        try:
            consumer = KafkaConsumer('new_raw_data_to_summarize',
                                     bootstrap_servers='kafka:9092',
                                     auto_offset_reset='earliest',
                                     enable_auto_commit=True,
                                     group_id='my-group',
                                     value_deserializer=lambda x: json.loads(x.decode('utf-8')))
            return consumer
        except NoBrokersAvailable:
            print("Broker not available, retrying...")
            time.sleep(3)


def consume_messages():
    consumer = create_consumer()

    for message in consumer:
        data = message.value['data']
        div_class = message.value['div_class']
        url = message.value['url']

        with app.app_context():
            result = extract_div_content(data, div_class).json
        if result.status_code == 200:  # Check the status code
            producer.send('summerized_data', {'url': url, 'data': summarize(result["data"])})
            produder.flush()
        else:
            print(result.json)

if __name__ == "__main__":
    producer = create_producer()
    consume_messages()
    app.run(debug=True, host='0.0.0.0',port=4040)


