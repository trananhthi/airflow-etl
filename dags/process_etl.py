
from airflow import DAG

from datetime import datetime, timedelta

# from airflow.operators.email import EmailOperator
from airflow.operators.python import PythonOperator
import pandas as pd
from sqlalchemy import create_engine

# Kết nối đến cơ sở dữ liệu PostgreSQL
# Thay đổi các thông số kết nối theo cấu hình của bạn
engine = create_engine('postgresql://admin:123456@my_postgres:5432/airflow_etl')

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 11, 12),
    'email_on_failure': True,
    'email_on_retry': True,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'email': ['trananhthi983@gmail.com'],
}


def extract_data_state(**kwargs):
    df_state = pd.read_excel('/opt/airflow/dataset/fake_dataset_state_20231112_081511.xlsx')
    data_dict = df_state.to_dict(orient='records')
    kwargs['ti'].xcom_push(key='state_data', value=data_dict)


def extract_data_card(**kwargs):
    df_card = pd.read_excel('/opt/airflow/dataset/fake_dataset_card_20231112_081511.xlsx')
    data_dict = df_card.to_dict(orient='records')
    kwargs['ti'].xcom_push(key='card_data', value=data_dict)


def extract(**kwargs):
    extract_data_state(**kwargs)
    extract_data_card(**kwargs)


def transform_data_state(**kwargs):
    ti = kwargs['ti']
    json_string_from_XCom = ti.xcom_pull(task_ids='extract', key='state_data')
    df_state = pd.DataFrame(json_string_from_XCom)
    df_transform = df_state.dropna()
    df_transform = df_transform.drop_duplicates(subset=['id'])
    df_transform = df_transform.drop_duplicates(subset=['state'])
    data_dict = df_transform.to_dict(orient='records')
    kwargs['ti'].xcom_push(key='state_data_transformed', value=data_dict)


def transform_data_card(**kwargs):
    ti = kwargs['ti']
    json_string_from_XCom = ti.xcom_pull(task_ids='extract', key='card_data')
    df_card = pd.DataFrame(json_string_from_XCom)
    df_transform = df_card.dropna()
    df_transform = df_transform.drop_duplicates(subset=['id card'])
    valid_genders = ['male', 'female']
    df_transform = df_transform[df_transform['gender'].isin(valid_genders)]
    current_year = pd.to_datetime('today').year
    df_transform = df_transform[df_transform['birth_year'].apply(lambda year: current_year - year >= 16)]
    df_transform = df_transform[df_transform['state'].between(1, 50)]
    data_dict = df_transform.to_dict(orient='records')
    kwargs['ti'].xcom_push(key='card_data_transformed', value=data_dict)


def transform(**kwargs):
    transform_data_state(**kwargs)
    transform_data_card(**kwargs)


def load_data_state(**kwargs):
    ti = kwargs['ti']
    json_string_from_XCom = ti.xcom_pull(task_ids='transform', key='state_data_transformed')
    df_state = pd.DataFrame(json_string_from_XCom)
    df_state.to_sql('states', engine, index=False, if_exists='replace')


def load_data_card(**kwargs):
    ti = kwargs['ti']
    json_string_from_XCom = ti.xcom_pull(task_ids='transform', key='card_data_transformed')
    df_card = pd.DataFrame(json_string_from_XCom)
    df_card.to_sql('IDcard', engine, index=False, if_exists='replace')


def load(**kwargs):
    load_data_state(**kwargs)
    load_data_card(**kwargs)


# def email_on_failure(context):
#     subject = f'DAG Failed: {context.get("dag_run").dag_id}'
#     body = f'The DAG {context.get("dag_run").dag_id} failed to run. Error details: {context.get("exception")}'
#     to = ['trananhthi983@gmail.com']
#
#     # Tạo một task EmailOperator để gửi email
#     email_task = EmailOperator(
#         task_id='send_failure_email',
#         to=to,
#         subject=subject,
#         html_content=f'<p>{body}</p>',
#         dag=context.get("dag"),
#     )
#     email_task.execute(context=context)


with DAG(
        dag_id='airflow-etl',
        default_args=default_args,
        schedule_interval="@monthly",

) as dag:
    extract_data = PythonOperator(
        task_id='extract',
        python_callable=extract,
        provide_context=True
    )
    transform_data = PythonOperator(
        task_id='transform',
        python_callable=transform,
        provide_context=True
    )
    load_data = PythonOperator(
        task_id='load',
        python_callable=load
    )
    # send_email_task = EmailOperator(
    #     task_id='send_email',
    #     to='trananhthi983@gmail.com',
    #     subject='Test Email from Airflow',
    #     html_content='<p>This is a test email sent from Apache Airflow.</p>',
    # )

extract_data >> transform_data >> load_data
