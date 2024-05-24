from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

@app.route('/extract', methods=['POST'])
def extract_div_content():
    data = request.get_json()
    url = data.get('url')
    div_class = data.get('div_class')

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)