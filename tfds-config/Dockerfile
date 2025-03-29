FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create a volume for YAML data files
VOLUME /app/app/data/data_files

CMD ["gunicorn", "--bind", "0.0.0.0:8005", "app:create_app()"]
