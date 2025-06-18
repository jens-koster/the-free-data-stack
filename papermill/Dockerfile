FROM freeds/spark-base:latest

WORKDIR /app
COPY requirements.txt /app/requirements.txt

# we're installing the freeds package here. we need to use the local python index.
RUN python3 -m pip install --trusted-host host.docker.internal --index-url http://host.docker.internal:8008/root/tfds/ --no-cache-dir -r requirements.txt


RUN python3 -m ipykernel install --user --name=TFDS --display-name "TFDS"
ENV TFDS_CONFIG_URL=http://tfds-config:8005/api/configs
ENV PATH="/home/spark/.local/bin:${PATH}"

COPY book_runner.py /app/book_runner.py

ENTRYPOINT []
