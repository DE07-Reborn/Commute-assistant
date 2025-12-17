import logging
from datetime import UTC, datetime, timedelta
from io import BytesIO, StringIO
import pandas as pd

from airflow import DAG
from airflow.exceptions import AirflowException
from airflow.operators.python import PythonOperator
from utils.basic_s3_utils import Basic_s3_utils

log = logging.getLogger(__name__)

S3_BUCKET = "commute-test-bucket"
S3_PATH = "raw_data/music"
S3_MUSIC_DATA_NAME = "music_origin_data"
S3_MUSIC_RESULT_DATA_NAME = "music_classified"


# 목적한 날짜와 시간의 데이터가 없을 때 발생시킬 오류
class DataNotFoundException(AirflowException):
    pass


# S3 조회에 실패할 경우 발생시킬 오류
class S3CheckError(AirflowException):
    pass


def bring_data_from_s3(bucket_name, bucket_path, music_data_name, **context):
    s3 = Basic_s3_utils(bucket=bucket_name)
    file_path = bucket_path + '/' + music_data_name
    df = s3.read(path=file_path)

    context['ti'].xcom_push(key="raw_df", value=df.to_json())

def music_data_classification(**context):
    raw_json = context['ti'].xcom_pull(task_ids="bring_data_from_s3", key="raw_df")
    df = pd.read_json(StringIO(raw_json))

    # tempo 기준 6개로 분할
    df_sorted = df.sort_values('tempo').reset_index(drop=True)
    df_sorted['tempo_group'] = (df_sorted.index // (len(df) // 6)) + 1

    # energy 기준 16개씩 분할
    sorted_dfs = {}

    for n in range(1, 7):
        sorted_dfs[n] = df_sorted[df_sorted['tempo_group'] == n].sort_values('energy', ascending=False).reset_index(drop=True)
        sorted_dfs[n]['energy_group'] = (sorted_dfs[n].index // (len(sorted_dfs[n]) // 16)) + 1
    
    result_df = pd.concat(sorted_dfs.values(), ignore_index=True)
    context['ti'].xcom_push(key="classified_df", value=result_df.to_json())

def music_classification_result_load(bucket_name, load_path, music_data_result_name, **context):
    classified_json = context['ti'].xcom_pull(task_ids="music_data_classification", key="classified_df")
    df = pd.read_json(StringIO(classified_json)).sort_values(by=['tempo_group', 'energy_group', 'popularity'], ascending=[True, True, False])
    file_path = load_path + music_data_result_name

    s3 = Basic_s3_utils(bucket=bucket_name)
    s3.upload(data=df, path=load_path, file_name=music_data_result_name)

with DAG(
    dag_id="music_classification_dag",
    start_date=datetime(2025, 12, 15),
    schedule_interval="@once",
    catchup=False,
    tags=["s3", "ELT", "music"],
    default_args={
        "owner": "airflow",
        "depends_on_past": False,
        "email_on_failure": False,
        "email_on_retry": False,
        "retries": 3,
        "retry_delay": timedelta(seconds=30),
    },
) as dag:
    # 1. S3에서 데이터 가져오기
    bring_data_from_s3_task = PythonOperator(
        task_id="bring_data_from_s3",
        python_callable=bring_data_from_s3,
        op_kwargs={
            "bucket_name": S3_BUCKET,
            "bucket_path": S3_PATH,
            "music_data_name": S3_MUSIC_DATA_NAME
        }
    )

    music_data_classification_task = PythonOperator(
        task_id="music_data_classification",
        python_callable=music_data_classification
    )

    music_classification_result_load_task = PythonOperator(
        task_id="music_classification_result_load",
        python_callable=music_classification_result_load,
        op_kwargs={
            "bucket_name": S3_BUCKET,
            "load_path": S3_PATH,
            "music_data_result_name": S3_MUSIC_RESULT_DATA_NAME
        }
    )

    bring_data_from_s3_task >> music_data_classification_task >> music_classification_result_load_task
