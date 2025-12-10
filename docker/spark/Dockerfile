FROM apache/spark:3.5.1

USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    gcc \
    && wget -qO - https://packages.confluent.io/deb/7.6/archive.key | apt-key add - \
    && echo "deb https://packages.confluent.io/deb/7.6 stable main" > /etc/apt/sources.list.d/confluent.list \
    && apt-get update \
    && apt-get install -y librdkafka-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /requirements.txt

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r /requirements.txt

WORKDIR /opt/spark/jobs

USER 1001
