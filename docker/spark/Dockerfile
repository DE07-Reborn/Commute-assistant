FROM bitnami/spark:3.5.1

USER root

COPY docker/spark/requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

WORKDIR /opt/spark/jobs
