import sys
import os

import boto3
from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

bucket_name = "houses-data-bucket-1232742434897"

url_template = 'http://prod.publicdata.landregistry.gov.uk.s3-website-eu-west-1.amazonaws.com/pp-monthly-update-new-version.csv'
AIRFLOW_HOME = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")
local_csv_path_template = AIRFLOW_HOME + '/data_houses.csv'

def s3_connection(filename, bucket_name, key):
    try:
        conn = boto3.resource('s3')
        conn.meta.client.upload_file(
            Filename=filename,
            Bucket=bucket_name,
            Key=key
        )
    except Exception as e:
        print(f'Falha ao conectar ao s3. Erro: {e}')
        sys.exit(1)


default_args = {
    "owner": "airflow",
    "start_date": days_ago(1),
    "depends_on_past": False,
    "retries": 1,
}

with DAG(
        dag_id='elt_houses_data_pipeline',
        description='Loading uk houses Data into Redshift',
        schedule_interval="@once",
        default_args=default_args,
        catchup=True,
        max_active_runs=1,
        tags=['Reddit'],
) as dag:
    download_data = BashOperator(
        task_id='download_data_in_docker',
        bash_command=f'curl {url_template} > {local_csv_path_template}',
        dag=dag
    )

    local_to_s3 = PythonOperator(
        task_id='loading_data_into_s3',
        python_callable=s3_connection,
        op_kwargs={
            'filename': local_csv_path_template,
            'bucket_name': bucket_name,
            'key': 'raw/data.csv'
        }
    )

    s3_to_redshift = BashOperator(
        task_id='loading_data_into_redshift',
        bash_command=f'python /opt/airflow/steps/s3_to_redshift.py',
        dag=dag
    )

download_data >> local_to_s3 >> s3_to_redshift
