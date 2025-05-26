FROM python:3.11-slim

WORKDIR /app
RUN apt-get update && apt-get install -y iputils-ping

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:8005", "app:create_app()"]
