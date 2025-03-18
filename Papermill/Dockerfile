# align with spark version, which is 3.5.0
FROM jupyter/pyspark-notebook:latest
# FROM python:3.11-slim-bookworm

COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
COPY book_runner.py /app/book_runner.py

RUN python -m ipykernel install --user
ENTRYPOINT ["python", "/app/book_runner.py"]
