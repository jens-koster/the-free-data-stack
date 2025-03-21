FROM apache/airflow:2.10.5
USER root
# dockerOperator needs docker installed in the container
RUN apt-get update && apt-get install -y docker.io
USER airflow

COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt
