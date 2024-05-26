import torch
from transformers import pipeline
from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import requests
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
import json
from database import SummarizedData,db,ma
import os
import time

summarizer = pipeline(
    "summarization",
    "pszemraj/long-t5-tglobal-base-16384-book-summary",
    device=0 if torch.cuda.is_available() else -1,
)



def summarize(text: str) -> str:
    return summarizer(text, max_length=200, min_length=50)[0]["summary_text"]

app = flask.Flask(__name__)

def extract_div_content(data, div_class):

    try:
        response = data

        if True:
            soup = BeautifulSoup(data, "html.parser")
            target_div = soup.find("div", {"class": div_class})

            if target_div:
                data = (
                    target_div.find("h2", class_="text-heading-large")
                    .text.strip()
                )
                
                return jsonify({
                    "data": data,
                })
            else:
                return jsonify({"error": f"Div with class '{div_class}' not found on the page."}), 404

        else:
            return jsonify({"error": f"Failed to retrieve the page. Status code: {response.status_code}"}), 500
    except:
        return jsonify({"error": "An error occurred while processing the request."}), 500

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
        with app.test_request_context():
            result = extract_div_content(data, div_class)
        if result:  # Check the status code
            text = result.get_json()

            if text:
                new_SummarizedData = SummarizedData(url,text["data"])
                with app.app_context():
                    db.session.add(new_SummarizedData)
                    db.session.commit()

if __name__ == "__main__":
    app.run(port=4040)

