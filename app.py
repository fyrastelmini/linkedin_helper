from flask import Flask, render_template, request, redirect, url_for
import os
import pandas as pd
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

def extract_div_content(url, div_class):
    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content of the page using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the specific div based on its ID
        target_div = soup.find('div', {'class': div_class})

        # Check if the div is found
        if target_div:
            # Extract and print the content of the div
            
            job_title = target_div.find('h1', class_='top-card-layout__title').text.strip().split('Login & Sign Up')[0]
            company_name = target_div.find('a', class_='topcard__org-name-link').text.strip()
            location = target_div.find('span', class_='topcard__flavor--bullet').text.strip()
            return({'job_title': job_title, 'company_name': company_name, 'location': location,'URL': url})
        else:
            print(f"Div with class '{div_class}' not found on the page.")
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/update_data', methods=['POST'])
def update_data():
    url = request.form['url']

    # Extract information from the URL
    div_class = "top-card-layout__entity-info-container flex flex-wrap papabear:flex-nowrap"
    text = extract_div_content(url, div_class)
    #text['URL'] = url

    # Load existing DataFrame or create a new one
    if os.path.exists('data.csv'):
        df = pd.read_csv('data.csv')
    else:
        df = pd.DataFrame(columns=['job_title', 'company_name', 'location', 'URL'])

    # Append new data to the DataFrame
    df = df.append(text, ignore_index=True)

    # Save the DataFrame to "data.csv"
    df.to_csv('data.csv', index=False)

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)