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
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from utils import extract_div_content, message_handler

# Create a global DataFrame to store the data
df_global = pd.DataFrame(columns=["job_title", "company_name", "location", "URL"])


app = Flask(__name__)
# configure the SQLite database, relative to the app instance folder
db_file_path = "/etc/volume/project.db"
#db_file_path = "project.db"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_file_path}"

# Create SQL database
db = SQLAlchemy(app)
ma = Marshmallow(app)


# Set the maximum file size to 20MB
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024


# Handle the RequestEntityTooLarge exception
@app.errorhandler(RequestEntityTooLarge)
def handle_file_size_too_large():
    # check if request type is POST
    if request.method == "POST":
        return redirect(url_for("main", upload="file_too_large"))
    abort(413)


class Job(db.Model):
    __tablename__ = "jobs_table"
    id = db.Column(db.Integer, primary_key=True)
    job_title = db.Column(db.String)
    company_name = db.Column(db.String)
    location = db.Column(db.String)
    URL = db.Column(db.String, unique=True)

    def __init__(self, job_title, company_name, location, URL) -> None:
        super(Job, self).__init__()
        self.job_title = job_title
        self.company_name = company_name
        self.location = location
        self.URL = URL

    def __repr__(self) -> str:
        return "<Job %r>" % self.job_title

class JobSchema(ma.Schema):
    class Meta:
        fields = ["id", "job_title", "company_name", "location", "URL"]





single_Job_data_schema = JobSchema()
multiple_Job_data_schema = JobSchema(many=True)

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

    # Send a POST request to the microservice
    response = requests.post('http://data_extractor:5000/extract', json={'url': url, 'div_class': div_class})

    # Check if the request was successful
    if response.status_code == 200:
        text = response.json()

        # Check if the text is not None
        if text:
            new_job = Job(
                text["job_title"], text["company_name"], text["location"], text["URL"]
            )
            db.session.add(new_job)
            db.session.commit()
            upload = "new_line_ok"
        else:
            upload = "new_line_no"
            print(text)
    else:
        upload = "new_line_no"
        print(f"Failed to retrieve data from microservice. Status code: {response.status_code}")

    return redirect(url_for("main", upload=upload))


@app.route("/view", methods=["GET"])
def view_db():
    all_jobs = Job.query.all()
    result = multiple_Job_data_schema.dump(all_jobs)
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
    app.run(host="0.0.0.0", port=8000, debug=True)
