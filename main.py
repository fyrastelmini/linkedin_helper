import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

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
            return({'job_title': job_title, 'company_name': company_name, 'location': location})
        else:
            print(f"Div with class '{div_class}' not found on the page.")
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")

# Example usage
url = 'https://ca.linkedin.com/jobs/view/data-scientist-login-sign-up-at-asana-3798552681?trk=public_jobs_topcard-title'
div_class="top-card-layout__entity-info-container flex flex-wrap papabear:flex-nowrap"
text = extract_div_content(url, div_class)
text['URL'] = url
if os.path.exists('data.csv'):
    # Load existing DataFrame from the CSV file
    df = pd.read_csv('data.csv')
    # Append new data to the existing DataFrame
else:
    # Create a new DataFrame
    df = pd.DataFrame(columns=['job_title', 'company_name', 'location', 'URL'])
    # Append new data to the new DataFrame
# update the DataFrame
df = df.append(text, ignore_index=True)
print(df)