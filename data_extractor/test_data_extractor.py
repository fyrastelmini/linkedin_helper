import pytest
from unittest.mock import patch, MagicMock
import os
from database import Job,db,ma
from data_extractor import extract_div_content, create_consumer, consume_messages

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
