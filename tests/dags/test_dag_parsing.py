from pathlib import Path

import pytest
from airflow.models import DagBag


# The path to DAGs *within the container*, though that should mirror the current
# directory structure.
DAG_FOLDER = Path(__file__).parents[2] / "openverse_catalog" / "dags"

# List of workflow files to test
# NOTE: If you've added a new provider, add the workflow filename here
PROVIDER_WORKFLOWS = [
    DAG_FOLDER / "providers" / workflow
    for workflow in [
        "brooklyn_museum_workflow.py",
        "check_new_smithsonian_unit_codes_workflow.py",
        "cleveland_museum_workflow.py",
        "europeana_ingestion_workflow.py",
        "europeana_workflow.py",
        "finnish_museums_workflow.py",
        "flickr_ingestion_workflow.py",
        "flickr_workflow.py",
        "metropolitan_museum_workflow.py",
        "museum_victoria_workflow.py",
        "nypl_workflow.py",
        "phylopic_workflow.py",
        "rawpixel_workflow.py",
        "science_museum_workflow.py",
        "smithsonian_workflow.py",
        "statens_museum_workflow.py",
        "walters_workflow.py",
        "wikimedia_ingestion_workflow.py",
        "wikimedia_workflow.py",
    ]
]

# Extra DAGs to test
ADDITIONAL_DAGS = [
    "maintenance/airflow_log_cleanup_workflow.py",
    "commoncrawl/sync_commoncrawl_workflow.py",
    "commoncrawl/commoncrawl_etl.py",
    "database/loader_workflow.py",
    "database/recreate_image_popularity_calculation.py",
    "database/refresh_all_image_popularity_data.py",
    "database/refresh_image_view_data.py",
    "oauth2/authorize_dag.py",
    "oauth2/token_refresh_dag.py",
]

# Expected count from the DagBag once a file has been parsed
# (this will likely not need to be edited for new providers)
EXPECTED_COUNT = {}


# relative_path represents the path from the DAG folder to the file
@pytest.mark.parametrize("relative_path", PROVIDER_WORKFLOWS + ADDITIONAL_DAGS)
def test_dag_loads_with_no_errors(relative_path, tmpdir):
    # Assume only 1 DAG is expected unless otherwise provided
    expected_count = EXPECTED_COUNT.get(relative_path, 1)
    dag_bag = DagBag(dag_folder=tmpdir, include_examples=False)
    dag_bag.process_file(str(DAG_FOLDER / relative_path))
    assert len(dag_bag.import_errors) == 0, "Errors found during DAG import"
    assert len(dag_bag.dags) == expected_count, "An unexpected # of DAGs was found"
