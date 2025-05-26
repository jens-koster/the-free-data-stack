FROM python:3.11-slim

WORKDIR /app
RUN apt-get update && apt-get install -y iputils-ping

COPY requirements.txt .
RUN pip install --trusted-host host.docker.internal --index-url http://host.docker.internal:8008/root/tfds/ --no-cache-dir -r requirements.txt
RUN mkdir -p /opt/tfds/
COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:8005", "app:create_app()"]
