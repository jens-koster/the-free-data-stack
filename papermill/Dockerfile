ARG TFDS_STACK_VERSION=1.0
FROM tfds/spark-base:latest

WORKDIR /app
COPY requirements.txt /app/requirements.txt


RUN pip install --no-cache-dir -r requirements.txt
RUN python3 -m ipykernel install --user --name=TFDS --display-name "TFDS"
ENV TFDS_CONFIG_URL=http://tfds-config:8005/api/configs
COPY book_runner.py /app/book_runner.py

ENTRYPOINT ["python3", "/app/book_runner.py"]
