# Library
# python tools
from datetime import timedelta
import pendulum

# Airflow
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup
from airflow import DAG

# Common utils
from utils.s3_utils import S3_utils
from utils.preprocessing_utils import Preprocessing
from utils.library_api_utils import Library_api_collector
from utils.kma_api_utils import Kma_api_collector


#######################
#      DAG METHODS    #
#######################

def request_daily_library_loan(**context):
    """
        Request daily book loan data from data4library
        Save JSON data into raw-data of S3
    """ 
    execution_date = context['logical_date']

    # Initialize library util and request API to get JSON
    ymd, hm = Preprocessing().split_time_context(execution_date)
    library_api = Library_api_collector(ymd)
    _json = library_api.request_loan_data()

    # Save JSON data into S3 folder: raw-data
    s3_connector = S3_utils(ymd, hm)
    s3_connector.upload(_json, 'raw-data/daily_library_loan')
    
    return _json


# Request Daily Weather API
def request_kma_daily_weather(**context):
    """
        Request daily weather data from kma
        Save pandas dataframe into raw-data of S3
    """ 
    execution_date = context['logical_date']

    # Initialize kma util
    ymd, hm = Preprocessing().split_time_context(execution_date)
    kma_api = Kma_api_collector(ymd, hm)

    # Read STN Metadata to get stn value of Seoul"(서울)
    s3_connector = S3_utils(ymd, hm)
    stn_meta = s3_connector.read('stn-metadata', 'csv')
    stn_id = kma_api.get_stn_number(stn_meta, '서울')
    
    # request API to get dataset with stn_id
    df = kma_api.request_daily_weather(stn_id)

    # Save JSON data into S3 folder: raw-data
    
    s3_connector.upload(df, 'raw-data/daily_kma_weather', 'csv')
    
    return df


# Preprocessing Daily Weather data
def preprocessing_kma_daily_weather(**context):
    """
        Preprocessing data
        Read kma daily weather data set from s3
        calling preprocessing methods to cleaning data set
        Save to s3 in preprocessed-data
    """

    # init Preprocessor
    preprocessor = Preprocessing()

    # Get dataset from s3
    execution_date = context['logical_date']
    ymd, hm = preprocessor.split_time_context(execution_date)
    
    s3_connector = S3_utils(ymd, hm)
    path = f'raw-data/daily_kma_weather/{ymd}/{hm}.csv'
    df = s3_connector.read(path, 'csv')

    # Preprocessing dataset
    new_df = preprocessor.preprocessing_kma_daily_weather(df)

    # Save into S3 : preprocessed-data
    s3_connector.upload(new_df, 'preprocessed-data/daily_kma_weather')

# Preprocessing Library Loan data
def preprocessing_daily_library_loan(**context):
    """
        Preprocessing data
        Read daily_library loan data set as csv from s3
        Calling preprocessing methods to cleaning data set 
        Save to s3 in preprocessed-data
    """

    # init preprocessor
    preprocessor = Preprocessing()

    # Get dataset from s3
    execution_date = context['logical_date']
    ymd, hm = preprocessor.split_time_context(execution_date)
    
    s3_connector = S3_utils(ymd, hm)
    path = f'raw-data/daily_library_loan/{ymd}/{hm}.json'
    df = s3_connector.read(path, 'json')

    # Preprocessing dataset
    new_df = preprocessor.preprocessing_daily_library_loan(df, ymd)

    # Save into S3 : preprocessed-data
    s3_connector.upload(new_df, 'preprocessed-data/daily_library_loan')


# Merge Two data
def merge_library_and_weather(**context):
    """
        After Preprocessing, merge daily library loan data and 
        daily kma weather data on each date column
        Then save on s3 :// data-model
    """

    # init preprocessor
    preprocessor = Preprocessing()

    # Get dataset from s3
    execution_date = context['logical_date']
    ymd, hm = preprocessor.split_time_context(execution_date)
    
    s3_connector = S3_utils(ymd, hm)

    library_path = f'preprocessed-data/daily_library_loan/{ymd}/{hm}.parquet'
    library_df = s3_connector.read(library_path)

    weather_path = f'preprocessed-data/daily_kma_weather/{ymd}/{hm}.parquet'
    weather_df = s3_connector.read(weather_path)

    merged = preprocessor.merge_dfs_on_date(weather_df, library_df)

    # Save to s3 -> data-model
    s3_connector.upload(merged, 'data-model')


# DAG INIT
# DAG Run everyday at 23:55
KST = pendulum.timezone("Asia/Seoul")
with DAG(
    dag_id = 'Load_daily_library_weather',
    start_date=pendulum.datetime(2025, 1, 1, 23, 50, tz=KST),
    schedule_interval="55 23 * * *",
    catchup = False,
    max_active_runs=1,
    tags=["kma", "metadata", "s3"],
) as dag:

    # Empty Operator to notice Dag initiates
    start = EmptyOperator(task_id = 'Start')

    # Task needs both library and kma api process to be done

    with TaskGroup('library_and_kma_flow') as library_and_kma_flow:

        # Library flow : Request API -> Save raw data in S3 -> Read then preprocessing
        with TaskGroup('library_flow') as library_flow:
            request_api = PythonOperator(
                task_id = 'request_daily_library_loan',
                python_callable = request_daily_library_loan,
                retries=1,
                retry_delay=timedelta(minutes=2),
            )

            preprocessing_library = PythonOperator(
                task_id = 'preprocessing_library',
                python_callable = preprocessing_daily_library_loan,
            )

            request_api >> preprocessing_library
        
        with TaskGroup('kma_flow') as kma_flow:
            request_api = PythonOperator(
                task_id = 'request_kma_daily_weather',
                python_callable = request_kma_daily_weather,
                retries=1,
                retry_delay=timedelta(minutes=2),
            )

            preprocessing_weather = PythonOperator(
                task_id = 'preprocessing_kma_daily_weather',
                python_callable = preprocessing_kma_daily_weather,
            )

            request_api >> preprocessing_weather

    with TaskGroup('merge') as merge:
        merge_dfs = PythonOperator(
            task_id = 'merge_two_datasets',
            python_callable = merge_library_and_weather
        )


    # Empty Operator to notice Dag Finishes
    finish = EmptyOperator(task_id = 'Finish')

    start >> library_and_kma_flow >> merge >> finish