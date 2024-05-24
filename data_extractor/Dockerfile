FROM python:3.9-slim-buster

WORKDIR /data_extractor

ADD ./data_extractor.py /data_extractor/data_extractor.py
ADD ./requirements.txt /data_extractor/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 5000

# Run app.py when the container launches
CMD ["python", "data_extractor.py"]