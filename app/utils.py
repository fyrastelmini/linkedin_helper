from bs4 import BeautifulSoup
import requests

# ______________________________ functions ______________________________________


# Function to extract the content of a specific div from a URL
def extract_div_content(url, div_class):
    # Send a GET request to the URL
    try:
        response = requests.get(url, timeout=5)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content of the page using BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")

            # Find the specific div based on its ID
            target_div = soup.find("div", {"class": div_class})

            # Check if the div is found
            if target_div:
                # Extract and print the content of the div

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
                return {
                    "job_title": job_title,
                    "company_name": company_name,
                    "location": location,
                    "URL": url,
                }
            else:
                print(f"Div with class '{div_class}' not found on the page.")

        else:
            print(f"Failed to retrieve the page. Status code: {response.status_code}")
    except:
        # return None if there is an error
        return None


# Function to handle different upload statuses
def message_handler(upload_status):
    if upload_status == "success":
        message = "File uploaded successfully"
    elif upload_status == "no_file":
        message = "No file uploaded, new file created"
    elif upload_status == "error":
        message = "Incorrect file, new file created"
    elif upload_status == "file_too_large":
        message = "Uploaded file is too large, new file created"
    elif upload_status == "empty":
        message = "Uploaded file is empty, new file created"
    elif upload_status == "new":
        message = "New file created successfully"
    elif upload_status == "new_line_ok":
        message = f"New line added successfully, current number of lines is: "
    elif upload_status == "new_line_no":
        message = f"Invalid line, current number of lines is: "
    else:
        message = ""
    return message
