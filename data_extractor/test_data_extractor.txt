import pytest
from unittest.mock import patch, MagicMock
import os
from database import Job,db,ma
import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
import json
import time

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
os.environ['DATABASE_URL'] = 'sqlite:////tmp/test.db'
from flask import Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
db.init_app(app)
ma.init_app(app)
def test_extract_div_content():
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = '<div class="test_class"><h1 class="top-card-layout__title">Job Title</h1><a class="topcard__org-name-link">Company Name</a><span class="topcard__flavor--bullet">Location</span></div>'
        result = extract_div_content('http://test.com', 'test_class')
        assert result.get_json() == {
            "job_title": "Job Title",
            "company_name": "Company Name",
            "location": "Location",
            "URL": 'http://test.com',
        }

def test_create_consumer():
    with patch('kafka.KafkaConsumer') as mock_kafka:
        mock_kafka.return_value = MagicMock()
        consumer = create_consumer()
        assert isinstance(consumer, MagicMock)

def test_consume_messages():
    with patch('data_extractor.create_consumer') as mock_create_consumer, \
         patch('data_extractor.extract_div_content') as mock_extract_div_content, \
         patch.object(db.session, 'add'), \
         patch.object(db.session, 'commit'):
        mock_message = MagicMock()
        mock_message.value = {'url': 'http://test.com', 'div_class': 'test_class'}
        mock_create_consumer.return_value = [mock_message]
        mock_extract_div_content.return_value = MagicMock()
        mock_extract_div_content.return_value.get_json.return_value = {
            "job_title": "Job Title",
            "company_name": "Company Name",
            "location": "Location",
            "URL": 'http://test.com',
        }
        consume_messages()
        mock_extract_div_content.assert_called_once_with('http://test.com', 'test_class')
