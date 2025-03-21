# """
# Documentation of pageview format: https://wikitech.wikimedia.org/wiki/Analytics/Data_Lake/Traffic/Pageviews
# """

from urllib import request

import airflow.utils.dates
import pendulum
import requests
from airflow import DAG
from airflow.exceptions import AirflowNotFoundException
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.sensors.python import PythonSensor

dag = DAG(
    dag_id="listing_4_20",
    start_date=pendulum.today("UTC").add(days=-1),
    schedule="3 * * * *",
    template_searchpath="/tmp",
    max_active_runs=1,
)


def make_url(execution_date) -> str:
    retrieve_date = execution_date.add(hours=-1)
    return (
        "https://dumps.wikimedia.org/other/pageviews/"
        f"{retrieve_date.year}/{retrieve_date.year}-{retrieve_date.month:0>2}/pageviews-{retrieve_date.year}{retrieve_date.month:0>2}{retrieve_date.day:0>2}-{retrieve_date.hour:0>2}0000.gz"
    )


def check_file_exists(execution_date) -> bool:
    url = make_url(execution_date)
    response = requests.head(url)
    return response.status_code == 200


wait_for_pageview_file = PythonSensor(
    task_id="wait_for_pageview_file",
    python_callable=check_file_exists,
    timeout=20 * 60,
    dag=dag,
)


create_table = SQLExecuteQueryOperator(
    task_id="create_table",
    conn_id="pg_pageviews",
    sql="""
    CREATE TABLE IF NOT EXISTS pageview_counts (
       pagename VARCHAR(50) NOT NULL,
       pageviewcount INT NOT NULL,
       datetime TIMESTAMP NOT NULL
    );
    """,
    dag=dag,
)


def _get_data(execution_date, output_path):
    url = make_url(execution_date)
    if not check_file_exists(execution_date=execution_date):
        raise AirflowNotFoundException(url)

    print("-" * 50)
    print(execution_date)
    print(url)
    request.urlretrieve(url, output_path)
    print("-" * 50)


get_data = PythonOperator(
    task_id="get_data",
    python_callable=_get_data,
    op_kwargs={
        "output_path": "/tmp/wikipageviews.gz",
    },
    dag=dag,
)


extract_gz = BashOperator(
    task_id="extract_gz", bash_command="gunzip --force /tmp/wikipageviews.gz", dag=dag
)


def _fetch_pageviews(pagenames, execution_date):
    result = dict.fromkeys(pagenames, 0)
    with open("/tmp/wikipageviews", "r") as f:
        for line in f:
            domain_code, page_title, view_counts, _ = line.split(" ")
            if domain_code == "en" and page_title in pagenames:
                result[page_title] = view_counts

    with open("/tmp/postgres_query.sql", "w") as f:
        for pagename, pageviewcount in result.items():
            f.write(
                "INSERT INTO pageview_counts VALUES ("
                f"'{pagename}', {pageviewcount}, '{execution_date}'"
                ");\n"
            )


fetch_pageviews = PythonOperator(
    task_id="fetch_pageviews",
    python_callable=_fetch_pageviews,
    op_kwargs={"pagenames": {"Google", "Amazon", "Apple", "Microsoft", "Facebook"}},
    dag=dag,
)

write_to_postgres = SQLExecuteQueryOperator(
    task_id="write_to_postgres",
    conn_id="pg_pageviews",
    sql="postgres_query.sql",
    dag=dag,
)

wait_for_pageview_file >> get_data >> extract_gz >> fetch_pageviews >> write_to_postgres
create_table >> write_to_postgres
