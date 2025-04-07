ARG TFDS_STACK_VERSION=1.0
FROM tfds/spark-base:${TFDS_STACK_VERSION}

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
RUN python -m ipykernel install --user
ENV TFDS_CONFIG_URL=http://tfds-config:8005/api/configs
COPY book_runner.py /app/book_runner.py

ENTRYPOINT ["python", "/app/book_runner.py"]
