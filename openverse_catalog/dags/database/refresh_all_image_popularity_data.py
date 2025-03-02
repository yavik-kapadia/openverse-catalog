"""
This file defines an Apache Airflow DAG that completely recalculates all
popularity data, including the percentile values, and also adding any
new popularity metrics.

This should be run at least once every 6 months, or whenever a new
popularity metric is added.
"""
import os
from datetime import datetime, timedelta

from airflow import DAG
from common import slack
from common.popularity import operators


DAG_ID = "refresh_all_image_popularity_data"
DB_CONN_ID = os.getenv("OPENLEDGER_CONN_ID", "postgres_openledger_testing")
MAX_ACTIVE_TASKS = 1
SCHEDULE_CRON = "@monthly"

DAG_DEFAULT_ARGS = {
    "owner": "data-eng-admin",
    "depends_on_past": False,
    "start_date": datetime(2020, 6, 15),
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(seconds=3600),
    "on_failure_callback": slack.on_failure_callback,
}


def create_dag(
    dag_id=DAG_ID,
    args=DAG_DEFAULT_ARGS,
    max_active_tasks=MAX_ACTIVE_TASKS,
    max_active_runs=MAX_ACTIVE_TASKS,
    schedule_cron=SCHEDULE_CRON,
    postgres_conn_id=DB_CONN_ID,
):
    dag = DAG(
        dag_id=dag_id,
        default_args=args,
        max_active_tasks=max_active_tasks,
        max_active_runs=max_active_runs,
        schedule_interval=schedule_cron,
        catchup=False,
        tags=["database"],
    )
    with dag:
        update_metrics = operators.update_media_popularity_metrics(postgres_conn_id)
        update_constants = operators.update_media_popularity_constants(postgres_conn_id)
        update_image_view = operators.update_db_view(postgres_conn_id)

        (update_metrics >> update_constants >> update_image_view)

    return dag


globals()[DAG_ID] = create_dag()
