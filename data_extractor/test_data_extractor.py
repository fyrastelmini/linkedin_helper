from flask.testing import FlaskClient
from data_extractor import app
from flask import json

def test_extract_div_content():
    client = app.test_client()
    div_class = (
        "top-card-layout__entity-info-container flex flex-wrap papabear:flex-nowrap"
    )
    url = "https://www.linkedin.com/jobs/view/3931418276/"
    data = {
        "url": url,
        "div_class": div_class
    }

    response = client.post('/extract', data=json.dumps(data), content_type='application/json')
    
    # Check that the status code is 200
    assert response.status_code == 200

    # Check that the response is a JSON object
    assert response.headers["Content-Type"] == "application/json"

    # Parse the JSON response
    json_response = json.loads(response.data)

    # Check that the JSON response has the expected structure
    # This depends on how your microservice is supposed to respond
    assert "job_title" in json_response
    assert "company_name" in json_response
    assert "location" in json_response
    assert "URL" in json_response

    # Check that the JSON response has the expected values
    assert json_response["job_title"] == "Ingénieur Data"
    assert json_response["company_name"] == "Innova Solutions"
    assert json_response["location"] == "Provence-Alpes-Côte d'Azur, France"
    assert json_response["URL"] == url
