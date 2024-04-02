from flask import Flask, render_template, request, redirect, url_for, send_file, abort
import pandas as pd
from bs4 import BeautifulSoup
import requests
from io import BytesIO
from werkzeug.exceptions import RequestEntityTooLarge


app = Flask(__name__)
# Create a global DataFrame to store the data
df_global = pd.DataFrame(columns=["job_title", "company_name", "location", "URL"])
# Set the maximum file size to 20MB
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024


# ______________________________ main routes _____________________________________
# Define the index route
@app.route("/")
def index():
    return render_template("index.html")


# Define the main route
@app.route("/main")
def main():
    upload_status = request.args.get("upload", "")
    message = message_handler(upload_status)

    # Pass the message to your template
    return render_template("main.html", message=message)


# ______________________________ data routes ______________________________________


# Define the upload_csv route
@app.route("/upload_csv", methods=["POST"])
def upload_csv():
    global df_global  # Use the global variable df_global

    # Check if a file was uploaded
    if "file" not in request.files:
        return redirect(url_for("main", upload="no_file"))

    file = request.files["file"]

    # Check if the file is not empty
    if file.filename == "":
        return redirect(url_for("main", upload="no_file"))
    if not file.filename.endswith(".csv"):
        return redirect(url_for("main", upload="error"))

    # Read the file once
    try:
        df = pd.read_csv(file, sep=";")
    except pd.errors.EmptyDataError:
        return redirect(url_for("main", upload="empty"))

    # Check the contents of the file
    if len(df) == 0:
        return redirect(url_for("main", upload="empty"))
    if not (df.columns == ["job_title", "company_name", "location", "URL"]).all():
        return redirect(url_for("main", upload="error"))

    # If everything is fine, store the DataFrame in df_global
    df_global = df

    return redirect(url_for("main", upload="success"))


# Define the update_data route
@app.route("/update_data", methods=["POST"])
def update_data():
    url = request.form["url"]

    # Extract information from the URL
    div_class = (
        "top-card-layout__entity-info-container flex flex-wrap papabear:flex-nowrap"
    )
    text = extract_div_content(url, div_class)
    global df_global

    # Check if the text is not None
    if not (text == None):
        text = pd.DataFrame([text], index=[0])
        df_global = pd.concat([df_global, text], ignore_index=True)
        df_global.drop_duplicates(inplace=True)
        upload = "new_line_ok"
    else:
        upload = "new_line_no"

    return redirect(url_for("main", upload=upload))


# Define the download_csv route
@app.route("/download_csv")
def download_csv():
    global df_global
    # Convert DataFrame to CSV
    csv_data = BytesIO()
    df_global.to_csv(csv_data, index=False, sep=";")
    csv_data.seek(0)

    # Send CSV data as file
    return send_file(
        csv_data, mimetype="text/csv", as_attachment=True, download_name="data.csv"
    )


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


# Handle the RequestEntityTooLarge exception
@app.errorhandler(RequestEntityTooLarge)
def handle_file_size_too_large():
    # check if request type is POST
    if request.method == "POST":
        return redirect(url_for("main", upload="file_too_large"))
    abort(413)


# Function to handle different upload statuses
def message_handler(upload_status):
    global df_global
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
        message = (
            f"New line added successfully, current number of lines is: {len(df_global)}"
        )
    elif upload_status == "new_line_no":
        message = f"Invalid line, current number of lines is: {len(df_global)}"
    else:
        message = ""
    return message


if __name__ == "__main__":
    app.run(debug=True)
