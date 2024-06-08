from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import requests
from kafka import KafkaConsumer,KafkaProducer
from kafka.errors import NoBrokersAvailable
import json
import os
import time

def create_producer():
    while True:
        try:
            producer = KafkaProducer(bootstrap_servers='kafka:9092',
                                     value_serializer=lambda v: json.dumps(v).encode('utf-8'))
            return producer
        except NoBrokersAvailable:
            print("Broker not available, retrying...")
            time.sleep(3)
app = Flask(__name__)

def extract_div_content(url, div_class):

    try:
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            target_div = soup.find("div", {"class": div_class})

            if target_div:
                job_title = (
                    target_div.find("h1", class_="top-card-layout__title")
                    .text.strip()
                    .split("Login & Sign Up")[0]
                )
                company_name = target_div.find(
                    "a", class_="topcard__org-name-link"
                ).text.strip()
                location = target_div.find(
                    "span", class_="topcard__flavor--bullet"
                ).text.strip()
                return jsonify({
                    "job_title": job_title,
                    "company_name": company_name,
                    "location": location,
                    "URL": url,
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
            consumer = KafkaConsumer('new_raw_data',
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
        url = message.value['url']
        div_class = message.value['div_class']
        with app.test_request_context():
            result = extract_div_content(url, div_class)
        if result:  # Check the status code
            text = result.get_json()

            if text:
                producer.send('extracted_data', {'job_title': text["job_title"], 'company_name': text["company_name"],'location' : text["location"],'url': url})
                producer.flush()
    
if __name__ == "__main__":
    producer = create_producer()
    consume_messages()
    app.run(debug=True, host='0.0.0.0', port=5000)