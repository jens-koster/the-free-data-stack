from datetime import datetime

from airflow.decorators import dag, task


@dag(start_date=datetime(2024, 1, 1), schedule="@daily", catchup=False)  # type: ignore[misc]
def simple_test_dag() -> None:
    @task  # type: ignore[misc]
    def hello() -> None:
        print("Hello from Airflow")

    hello()


dag = simple_test_dag()
