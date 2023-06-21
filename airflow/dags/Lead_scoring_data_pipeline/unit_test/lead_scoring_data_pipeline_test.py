##############################################################################
# Import necessary modules
# #############################################################################


from airflow import DAG
from airflow.operators.python import PythonOperator

from datetime import datetime, timedelta
from Lead_scoring_data_pipeline.unit_test.utils import *
from Lead_scoring_data_pipeline.unit_test.data_validation_checks import *
from Lead_scoring_data_pipeline.unit_test.test_with_pytest import *

###############################################################################
# Define default arguments and DAG
# ##############################################################################

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2022,7,30),
    'retries' : 1, 
    'retry_delay' : timedelta(seconds=5)
}


ML_data_cleaning_dag = DAG(
                dag_id = 'Lead_Scoring_Data_Engineering_Pipeline_test',
                default_args = default_args,
                description = 'DAG to run data pipeline for lead scoring Test cases',
                schedule_interval = '@daily',
                catchup = False
)

###############################################################################
# Create a task for build_dbs() function with task_id 'building_db'
# ##############################################################################
building_db_test = PythonOperator(
            task_id = 'building_db_test',
            python_callable = test_load_data_into_db,
            dag = ML_data_cleaning_dag)
###############################################################################
# Create a task for map_city_tier() function with task_id 'mapping_city_tier'
###############################################################################
mapping_city_tier_test = PythonOperator(
            task_id = 'mapping_city_tier_test',
            python_callable = test_map_city_tier,
            dag = ML_data_cleaning_dag)
###############################################################################
# Create a task for map_categorical_vars() function with task_id 'mapping_categorical_vars'
###############################################################################
mapping_categorical_vars_test = PythonOperator(
        task_id = 'mapping_categorical_vars_test',
        python_callable = test_map_categorical_vars,
        dag = ML_data_cleaning_dag)
###############################################################################
# Create a task for interactions_mapping() function with task_id 'mapping_interactions'
###############################################################################
mapping_interactions_test = PythonOperator(
        task_id = 'mapping_interactions_test',
        python_callable = test_interactions_mapping,
        dag = ML_data_cleaning_dag)
###############################################################################
# Define the relation between the tasks
###############################################################################


building_db_test >> mapping_city_tier_test  >> mapping_categorical_vars_test >> mapping_interactions_test
