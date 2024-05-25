# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD ./app.py /app/app.py
ADD ./utils.py /app/utils.py
ADD ./database.py /app/database.py
ADD ./requirements.txt /app/requirements.txt
ADD ./templates /app/templates

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 8000

# Run app.py when the container launches
CMD ["python", "app.py"]