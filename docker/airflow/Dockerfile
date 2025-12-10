FROM apache/airflow:2.9.1-python3.11

USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY docker/airflow/requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

WORKDIR /opt/airflow

EXPOSE 8080

CMD ["airflow", "standalone"]