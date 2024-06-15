from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime,timedelta
from airflow.operators.python_operator import PythonOperator
import psycopg2
from airflow_dbt.operators.dbt_operator import DbtRunOperator

def load_data():
    conn = psycopg2.connect(dbname='target_db', user='target_user', password='target_password', host='target_db')
    cur = conn.cursor()

    cur.execute("CREATE TEMP TABLE tmp_table (LIKE jobs_table_joined INCLUDING DEFAULTS);")
    with open('/tmp/jobs_table_joined.csv', 'r') as f:
        cur.copy_expert("COPY tmp_table FROM STDIN WITH CSV DELIMITER ','", f)
    cur.execute("INSERT INTO jobs_table_joined SELECT * FROM tmp_table ON CONFLICT (id) DO NOTHING;")
    cur.execute("DROP TABLE tmp_table;")

    conn.commit()
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2022, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}
dag = DAG(
    'copy_view', 
    default_args=default_args,
    description='Update targetdb DAG',
    schedule_interval=timedelta(minutes=5),
    is_paused_upon_creation=False
)

export_task = BashOperator(
    task_id='export_view',
    bash_command="""
    PGPASSWORD=source_password psql -h source_db -U source_user -d source_db -c "\\copy (SELECT * FROM jobs_table_joined) To '/tmp/jobs_table_joined.csv' With CSV"
    """,
    dag=dag,
)
import_task = PythonOperator(
    task_id='import_view',
    python_callable=load_data,
    dag=dag,
)


create_table_task = BashOperator(
    task_id='create_table',
    bash_command="""
    PGPASSWORD=target_password psql -h target_db -U target_user -d target_db -c "CREATE TABLE IF NOT EXISTS jobs_table_joined (
        id SERIAL PRIMARY KEY,
        job_title VARCHAR(255),
        company_name VARCHAR(255),
        location VARCHAR(255),
        URL VARCHAR(1000) UNIQUE,
        summarized_data TEXT
    );"
    """,
    dag=dag,
)

dbt_run = DbtRunOperator(
    task_id='dbt_task',
    profiles_dir='/dbt/profiles',
    dir='/dbt/',
    dag=dag,
)
create_table_task >> export_task >> import_task >> dbt_run