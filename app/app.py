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
import requests
from werkzeug.exceptions import RequestEntityTooLarge
from utils import message_handler
from kafka import KafkaProducer, KafkaConsumer
import json
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

# Initialize Kafka consumer
def create_consumer():
    while True:
        try:
            consumer = KafkaConsumer('database_view',
                                     bootstrap_servers='kafka:9092',
                                     auto_offset_reset='earliest',
                                     enable_auto_commit=True,
                                     group_id='my-group',
                                     value_deserializer=lambda x: json.loads(x.decode('utf-8')))
            return consumer
        except NoBrokersAvailable:
            print("Broker not available, retrying...")
            time.sleep(3)




app = Flask(__name__)


# Set the maximum file size to 20MB
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024


# Handle the RequestEntityTooLarge exception
@app.errorhandler(RequestEntityTooLarge)
def handle_file_size_too_large():
    # check if request type is POST
    if request.method == "POST":
        return redirect(url_for("main", upload="file_too_large"))
    abort(413)


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
    return "not implemented yet"
    """
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
    """


# Define the update_data route
@app.route("/update_data", methods=["POST"])
def update_data():
    url = request.form["url"]

    # Define the div class
    div_class = (
        "top-card-layout__entity-info-container flex flex-wrap papabear:flex-nowrap"
    )
    div_class_summarize = (
        "show-more-less-html__markup show-more-less-html__markup--clamp-after-5 relative overflow-hidden"
    )
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        html_content = response.text
        # Send a message to the Kafka topics
        producer.send('new_raw_data', {'url': url, 'div_class': div_class,'raw_data':html_content})
        producer.send('new_raw_data_to_summarize', {'url': url, 'data': html_content, 'div_class': div_class_summarize})
        producer.flush()
        return redirect(url_for("main", upload="ok"))
    return redirect(url_for("main", upload="error"))
    


@app.route("/view", methods=["GET"])
def view_db():
    #all_jobs = Job.query.all()
    #result = multiple_Job_data_schema.dump(all_jobs)
    #all_raw = RawData.query.all()
    #result = multiple_RawData_data_schema.dump(all_raw)
    #all_summarized = SummarizedData.query.all()
    #result = multiple_SummarizedData_data_schema.dump(all_summarized)
    #return jsonify(result)
    return "not implemented yet"


# Define the download_csv route
@app.route("/download_csv")
def download_csv():
    return "not implemented yet"
    """
    global df_global
    # Convert DataFrame to CSV
    csv_data = BytesIO()
    df_global.to_csv(csv_data, index=False, sep=";")
    csv_data.seek(0)

    # Send CSV data as file
    return send_file(
        csv_data, mimetype="text/csv", as_attachment=True, download_name="data.csv"
    )"""


if __name__ == "__main__":
    producer = create_producer()
    app.run(host="0.0.0.0", port=8000, debug=True)
