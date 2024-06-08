FROM python:3.9-slim-buster

WORKDIR /summarizer

ADD ./summarizer.py /summarizer/summarizer.py
ADD ./requirements.txt /summarizer/requirements.txt


RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 4040

# Run app.py when the container launches
CMD ["python", "summarizer.py"]