from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    send_file,
    abort,
    jsonify,
)
import pandas as pd
from bs4 import BeautifulSoup
import requests
from io import BytesIO
from werkzeug.exceptions import RequestEntityTooLarge
from database import db, ma, Job, JobSchema
from utils import extract_div_content, message_handler
from database import db, ma, Job, JobSchema, RawData, RawDataSchema, single_Job_data_schema, multiple_Job_data_schema, single_RawData_data_schema, multiple_RawData_data_schema
from kafka import KafkaProducer
import json
import os
from kafka.errors import NoBrokersAvailable
import time

# Initialize Kafka producer
def create_producer():
    while True:
        try:
            producer = KafkaProducer(bootstrap_servers='kafka:9092',
                                     value_serializer=lambda v: json.dumps(v).encode('utf-8'))
            return producer
        except NoBrokersAvailable:
            print("Broker not available, retrying...")
            time.sleep(3)




# Create a global DataFrame to store the data
df_global = pd.DataFrame(columns=["job_title", "company_name", "location", "URL"])


app = Flask(__name__)
# configure the SQLite database, relative to the app instance folder
db_file_path = "/etc/volume/project.db"
#db_file_path = "project.db"
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('DATABASE_URL')

# Initialize the database with the app
db.init_app(app)
ma.init_app(app)


# Set the maximum file size to 20MB
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024


# Handle the RequestEntityTooLarge exception
@app.errorhandler(RequestEntityTooLarge)
def handle_file_size_too_large():
    # check if request type is POST
    if request.method == "POST":
        return redirect(url_for("main", upload="file_too_large"))
    abort(413)



with app.app_context():
    db.create_all()


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

    return redirect(url_for("main", upload="success"))


# Define the update_data route
@app.route("/update_data", methods=["POST"])
def update_data():
    url = request.form["url"]

    # Define the div class
    div_class = (
        "top-card-layout__entity-info-container flex flex-wrap papabear:flex-nowrap"
    )
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        html_content = response.text
        new_raw_data = RawData(source=url, raw_data=html_content)
        db.session.add(new_raw_data)
    # Send a message to the Kafka topic
    producer.send('new_raw_data', {'url': url, 'div_class': div_class})
    return redirect(url_for("main", upload="ok"))

    


@app.route("/view", methods=["GET"])
def view_db():
    all_jobs = Job.query.all()
    result = multiple_Job_data_schema.dump(all_jobs)
    #all_raw = RawData.query.all()
    #result = multiple_RawData_data_schema.dump(all_raw)
    return jsonify(result)


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


if __name__ == "__main__":
    producer = create_producer()
    app.run(host="0.0.0.0", port=8000, debug=True)
