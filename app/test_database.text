import pytest
from flask import Flask
from database import Job,RawData, db, ma

@pytest.fixture
def test_app():
    # Create a new Flask application
    app = Flask(__name__)
    # Configure the application for testing
    app.config["TESTING"] = True

    # Configure the application to use an in-memory SQLite database for testing
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    # Initialize db and ma with the test app
    db.init_app(app)
    ma.init_app(app)



    # Create all database tables
    with app.app_context():
        db.create_all()
        

    yield app

    # Drop all database tables after the test is complete
    with app.app_context():
        db.drop_all()

def test_database(test_app):
    # Create a test client using the Flask application
    with test_app.test_client() as client:
        # Create a new app context for the test
        with test_app.app_context():
            # Create all database tables
            db.create_all()

            # Create a new Job object
            new_job = Job("Software Engineer", "Company", "Location", "https://www.example.com")

            # Add the new job to the database
            db.session.add(new_job)
            db.session.commit()

            # Retrieve the job from the database
            job = Job.query.filter_by(URL="https://www.example.com").first()

            # Check that the job was correctly added to the database
            assert job is not None
            assert job.job_title == "Software Engineer"
            assert job.company_name == "Company"
            assert job.location == "Location"
            assert job.URL == "https://www.example.com"

            # Same for RawData objects

            # Create a new RawData object
            new_raw_data = RawData("Source","BLABLABLA")

            # Add the new raw data to the database
            db.session.add(new_raw_data)
            db.session.commit()

            rawdata = RawData.query.filter_by(source="Source").first()

            assert rawdata is not None
            assert rawdata.source == "Source"
            assert rawdata.raw_data == "BLABLABLA"

            # Drop all database tables
            db.drop_all()