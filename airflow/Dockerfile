FROM apache/airflow:2.2.4-python3.8

ENV AIRFLOW_HOME=/opt/airflow

USER root

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
         vim \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

USER airflow

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

SHELL ["/bin/bash", "-o", "pipefail", "-e", "-u", "-x", "-c"]

USER $AIRFLOW_UID