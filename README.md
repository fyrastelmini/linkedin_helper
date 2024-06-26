# LinkedIn Data Extractor
![Test app](https://github.com/fyrastelmini/linkedin_helper/actions/workflows/main_app.yml/badge.svg)
![Database CI](https://github.com/fyrastelmini/linkedin_helper/actions/workflows/database.yml/badge.svg)
![Deploy](https://github.com/fyrastelmini/linkedin_helper/actions/workflows/docker-image.yml/badge.svg)

LinkedIn Data Extractor is a tool that allows you to extract data from LinkedIn job postings using their URL. The data is ingested from multiple sources (different microservices of this project) into a first postgres database and passes through a fully automated ELT pipeline. The transformed data is then loaded into a second postgres database that communicates with the main application and provides clean views of the data.
## API Structure
![Microservices and API structure](images/API_diagram.png)
## Data Engineering pipeline
![ELT Pipeline](images/ELT.png)
## Running the project

Clone this repository to your local/host machine:
```bash
git clone https://github.com/fyrastelmini/linkedin_helper.git
```


Navigate into the project directory:
```bash
cd linkedin_helper
```

Build and run the containers:
```bash
docker-compose up
```

Linting, formatting and testing are also present within the Makefile

## Usage

To use LinkedIn Data Extractor, follow these steps:

Launch the application.
Either upload a .csv file with the following columns:
| job_title | company_name | location | URL |
|-----------|--------------|----------|-----|
| title #1  | company #1   | location #1 | URL #1 |
| title #2  | company #2   | location #2 | URL #2 |


Or just click on the "Create new" button.

Enter the URL of the LinkedIn job posting you want to extract data from. The link should be of this form:
https://www.linkedin.com/jobs/view/<job_id>/?* or https://www.linkedin.com/jobs/view/<job_id>
( <job_id> is an integer )

Click on "Update Data" to extract the data. A dataframe will be updated within the container with the new lines corresponding to the job's info.

Click on "Save" to save the extracted data to a CSV file.

Uploading files larger than 20mb would result in an error, additionally, the app handles incorrect file formats/columns/names by simply initializing a new file without uploading the problematic data.

## Contributing
Contributions to this project are welcome. If you would like to contribute, please fork the repository and submit a pull request.

## License
This project is licensed under the terms of the MIT license. See the LICENSE file for details.
