from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

# Create SQL database
db = SQLAlchemy()
ma = Marshmallow()

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

class RawData(db.Model):
    __tablename__ = "raw_data_table"
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String)
    raw_data = db.Column(db.Text)

    def __init__(self,source, raw_data) -> None:
        super(RawData, self).__init__()
        self.source = source
        self.raw_data = raw_data

    def __repr__(self) -> str:
        return "<RawData %r>" % self.raw_data
    
class RawDataSchema(ma.Schema):
    class Meta:
        fields = ["id", "source", "raw_data"]

single_RawData_data_schema = RawDataSchema()
multiple_RawData_data_schema = RawDataSchema(many=True)

class SummarizedData(db.Model):
    __tablename__ = "summarized_data_table"
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String)
    summarized_data = db.Column(db.Text)

    def __init__(self,source, summarized_data) -> None:
        super(SummarizedData, self).__init__()
        self.source = source
        self.summarized_data = summarized_data

    def __repr__(self) -> str:
        return "<SummarizedData %r>" % self.summarized_data

class SummarizedDataSchema(ma.Schema):
    class Meta:
        fields = ["id", "source", "summarized_data"]

single_SummarizedData_data_schema = SummarizedDataSchema()
multiple_SummarizedData_data_schema = SummarizedDataSchema(many=True)