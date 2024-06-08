FROM python:3.9-slim-buster

WORKDIR /database_handler

ADD ./database_handler.py /database_handler/database_handler.py
ADD ./database.py /database_handler/database.py
ADD ./requirements.txt /database_handler/requirements.txt


RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 4444

# Run app.py when the container launches
CMD ["python", "database_handler.py"]