FROM python:3.7-slim

COPY elt_script.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "elt_script.py"]