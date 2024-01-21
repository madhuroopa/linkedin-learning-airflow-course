import pandas as pd
import datetime 
from datetime import datetime,timedelta
from airflow.utils.dates import days_ago
from airflow import DAG
from airflow.operators.python_operator import PythonOperator


default_args ={
    'owner':'madhu'
}

def read_csv_file():
    df = pd.read_csv('/home/mirukulla/airflow/datasets/insurance.csv')
    print(df)
    return df.to_json()
def clean_null_values(ti):
   # ti = kwargs['ti']
    json_data = ti.xcom_pull(task_ids='read_csv_file')
    df = pd.read_json(json_data)
    df = df.dropna()    
    print(df)
    return df.to_json()
def groupby_smoke(ti):
    json_data = ti.xcom_pull(task_ids='clean_null_values')
    df = pd.read_json(json_data)
    smoker_df = df.groupby('smoker').agg({
        'age':'mean',
        'bmi':'mean',
        'charges':'mean'
    }).reset_index()
    smoker_df.to_csv("/home/mirukulla/airflow/output/grouped_by_smoker.csv",index=False)
def groupby_region(ti):
    json_data = ti.xcom_pull(task_ids='clean_null_values')
    df = pd.read_json(json_data)
    region_df = df.groupby('region').agg({
        'age':'mean',
        'bmi':'mean',
        'charges':'mean'
    }).reset_index()
    region_df.to_csv('/home/mirukulla/airflow/output/grouped_by_region.csv',index=False)
with DAG(
    dag_id = 'python_pipeline',
    description = 'Running a Python pipeline',
    default_args = default_args,
    start_date = days_ago(1),
    schedule_interval = '@once',
    tags = ['python', 'transform', 'pipeline']
) as dag:
    
    read_csv_file = PythonOperator(
        task_id='read_csv_file',
        python_callable = read_csv_file
    )
    clean_null_values=PythonOperator(
        task_id='clean_null_values',
        python_callable=clean_null_values
    )
    grouped_by_smoker=PythonOperator(
        task_id='grouped_by_smoker',
        python_callable=groupby_smoke
    )
    grouped_by_region=PythonOperator(
        task_id='grouped_by_region',
        python_callable=groupby_region
    )
    read_csv_file >> clean_null_values >> [grouped_by_smoker,grouped_by_region]