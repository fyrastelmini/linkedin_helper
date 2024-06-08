import pytest
import requests_mock
from data_extractor import app, extract_div_content

def test_extract_div_content():
    with requests_mock.Mocker() as m:
        # Simulate a GET request to 'http://test.com'
        m.get('http://test.com', text='<div class="test-class"><h1 class="top-card-layout__title">Job Title</h1><a class="topcard__org-name-link">Company Name</a><span class="topcard__flavor--bullet">Location</span></div>')

        with app.app_context():
            # Call the function with the test URL and div class
            response = extract_div_content('http://test.com', 'test-class')

        # Check the status code
        assert response.status_code == 200

        # Check the response data
        data = response.get_json()
        assert data['job_title'] == 'Job Title'
        assert data['company_name'] == 'Company Name'
        assert data['location'] == 'Location'
        assert data['URL'] == 'http://test.com'
