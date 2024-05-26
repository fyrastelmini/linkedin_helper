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
    long_text = "Summerize the key requirements for applying to this Job offer: "+text
    return summarizer(long_text)[0]["summary_text"]

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
db.init_app(app)
ma.init_app(app)

def extract_div_content(data, div_class):
    if True:
        soup = BeautifulSoup(data, "html.parser")
        target_div = soup.find("div", {"class": div_class})

        if target_div:
            data = target_div.text.strip()
                
            return jsonify({
                "data": data 
            })
        else:
            return jsonify({"error": f"Div with class '{div_class}' not found on the page."}), 404


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
        if result.status_code == 200:  # Check the status code
            text = result.get_json()

            if text:
                new_SummarizedData = SummarizedData(url,summarize(text["data"]))
                with app.app_context():
                    db.session.add(new_SummarizedData)
                    db.session.commit()
                print(text)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    consume_messages()
    app.run(debug=True, host='0.0.0.0',port=4040)


