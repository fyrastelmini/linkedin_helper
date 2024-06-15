# Dockerfile
FROM apache/airflow:2.1.2

# Switch to root user to install dependencies
USER root

# Install gcc and other dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Switch back to airflow user
USER airflow

# Install dbt
RUN pip install dbt airflow_dbt