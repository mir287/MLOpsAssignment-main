###############################################################################
#Import necessary modules
############################################################################## 


from Lead_scoring_data_pipeline.constants import *
from Lead_scoring_data_pipeline.utils import *
from Lead_scoring_data_pipeline.schema import *

import pandas as pd


###############################################################################
# Define function to validate raw data's schema
############################################################################### 

def raw_data_schema_check():
    '''
    This function check if all the columns mentioned in schema.py are present in
    leadscoring.csv file or not.

   
    INPUTS
        db_file_name : Name of the database file
        db_path : path where the db file should be   
        raw_data_schema : schema of raw data in the form oa list/tuple as present 
                          in 'schema.py'

    OUTPUT
        If the schema is in line then prints 
        'Raw datas schema is in line with the schema present in schema.py' 
        else prints
        'Raw datas schema is NOT in line with the schema present in schema.py'

    
    SAMPLE USAGE
        raw_data_schema_check
    '''
    df_raw_data = pd.read_csv(DATA_DIRECTORY+'leadscoring.csv')
    
    check = set(df_raw_data.columns) == set(raw_data_schema)
    if check:
        logging.info('Raw datas schema is in line with the schema present in schema.py')
    else:
        logging.warning('Raw datas schema is NOT in line with the schema present in schema.py')

###############################################################################
# Define function to validate model's input schema
############################################################################### 

def model_input_schema_check():
    '''
    This function check if all the columns mentioned in model_input_schema in 
    schema.py are present in table named in 'model_input' in db file.

   
    INPUTS
        db_file_name : Name of the database file
        db_path : path where the db file should be   
        raw_data_schema : schema of models input data in the form oa list/tuple
                          present as in 'schema.py'

    OUTPUT
        If the schema is in line then prints 
        'Models input schema is in line with the schema present in schema.py'
        else prints
        'Models input schema is NOT in line with the schema present in schema.py'
    
    SAMPLE USAGE
        raw_data_schema_check
    '''
    cnx = sqlite3.connect(DB_PATH+DB_FILE_NAME)
    
    df_model_input = pd.read_sql('select * from model_input', cnx)
    
    logging.info(DB_PATH+DB_FILE_NAME)
    logging.info('******* Checking Column Info *********')
    logging.info(df_model_input.columns)
    logging.info(model_input_schema)

    check = set(df_model_input.columns) == set(model_input_schema)
    if check:
        logging.info('Models input schema is in line with the schema present in schema.py')
    else:
        logging.warning('Models input schema is NOT in line with the schema present in schema.py')

    
    
