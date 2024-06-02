from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import requests
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
import json
from database import Job,db,ma
import os
import time


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

def init_db():
    db.init_app(app)
    ma.init_app(app)
init_db()
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
                new_job = Job(text["job_title"], text["company_name"], text["location"], text["URL"])
                with app.app_context():
                    db.session.add(new_job)
                    db.session.commit()
    
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    consume_messages()
    app.run(debug=True, host='0.0.0.0', port=5000)