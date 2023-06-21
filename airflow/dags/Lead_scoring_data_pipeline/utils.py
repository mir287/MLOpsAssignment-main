###############################################################################
# Import necessary modules
# Update by Richard K on 06/16/2023
##############################################################################
import pandas as pd
import os

from Lead_scoring_data_pipeline.mapping.city_tier_mapping import city_tier_mapping
from Lead_scoring_data_pipeline.mapping.significant_categorical_level import *
from Lead_scoring_data_pipeline.constants import *

import sqlite3
from sqlite3 import Error
import logging


################################################################################
# Define the function to build database
###############################################################################
def build_dbs():
    '''
    This function checks if the db file with specified name is present 
    in the specified path. If it is not present it created the db file 
    with the given name at the given path.


    INPUTS
        db_file_name : Name of the database file
        db_path : path where the db file should be   


    OUTPUT
    The function returns the following under the conditions:
        1. If the file exists at the specified path
                prints 'DB Already Exists' and returns 'DB Exists'

        2. If the db file is not present at the specified loction
                prints 'Creating Database' and creates the sqlite db 
                file at the specified path with the specified name and 
                once the db file is created prints 'New DB Created' and 
                returns 'DB created'


    SAMPLE USAGE
        build_dbs()
        
    NOTE 
        Here you can simply use the build_dbs function you used in the previous
        modules 
    '''
    print("DBPath" + DB_PATH+DB_FILE_NAME)
    if os.path.isfile(DB_PATH+DB_FILE_NAME):
        logging.info('******* DB Already Exsist i above location *********')
        return "DB Exsists"
    else:
        logging.info('******* Creating New Database *********')
        """ create a database connection to a SQLite database """
        conn = None
        try:
            conn = sqlite3.connect(DB_PATH+DB_FILE_NAME)
            logging.info('******* New DB Created in specified location *********')
        except Error as e:
            logging.error(e)
            return "Error"
        finally:
            if conn:
                conn.close()
                return "DB Created"


###############################################################################
# Define function to load the csv file to the database
###############################################################################

def load_data_into_db():
    '''
    This function loads the data present in data directiry into the db
    which was created previously.
    It also replaces any null values present in 'total_leads_dropped' and
    'referred_lead' with 0.


    INPUTS
        db_file_name : Name of the database file
        db_path : path where the db file should be
        data_directory : path of the directory where 'leadscoring.csv' 
                        file is present
        

    OUTPUT
        Saves the processed dataframe in the db in a table named 'loaded_data'.
        If the table with the same name already exsists then the function 
        replaces it.


    SAMPLE USAGE
        load_data_into_db()
    '''
    cnx = sqlite3.connect(DB_PATH+DB_FILE_NAME)
    
    # swappng between inference vs actual score 
    #df_lead_scoring = pd.read_csv(DATA_DIRECTORY+'leadscoring_inference.csv')
    df_lead_scoring = pd.read_csv(DATA_DIRECTORY+'leadscoring.csv')

    df_lead_scoring['total_leads_droppped'] = df_lead_scoring['total_leads_droppped'].fillna(0)
    df_lead_scoring['referred_lead'] = df_lead_scoring['referred_lead'].fillna(0)

    df_lead_scoring.to_sql(name='loaded_data', con=cnx, if_exists='replace', index=False)

    logging.info('******* Checking df_lead_scoring Column Info *********')
    logging.info(df_lead_scoring.columns)
    
    # If need you can write the csv file to check the data 
    #df_lead_scoring.to_csv('df_lead_scoring.csv', index=False)
    cnx.close()

###############################################################################
# Define function to map cities to their respective tiers
###############################################################################

    
def map_city_tier():
    '''
    This function maps all the cities to their respective tier as per the
    mappings provided in /mappings/city_tier_mapping.py file. If a
    particular city's tier isn't mapped in the city_tier_mapping.py then
    the function maps that particular city to 3.0 which represents
    tier-3.


    INPUTS
        db_file_name : Name of the database file
        db_path : path where the db file should be
        city_tier_mapping : a dictionary that maps the cities to their tier 
        which is already imported at the beginning of the file

    
    OUTPUT
        Saves the processed dataframe in the db in a table named
        'city_tier_mapped'. If the table with the same name already 
        exists then the function replaces it.

    
    SAMPLE USAGE
        map_city_tier()

    '''
    cnx = sqlite3.connect(DB_PATH+DB_FILE_NAME)

    df_lead_scoring = pd.read_sql('select * from loaded_data', cnx)

    df_lead_scoring["city_tier"] = df_lead_scoring["city_mapped"].map(
        city_tier_mapping)
    df_lead_scoring["city_tier"] = df_lead_scoring["city_tier"].fillna(3.0)
    df_lead_scoring = df_lead_scoring.drop(['city_mapped'], axis=1)

    df_lead_scoring.to_sql(name='city_tier_mapped', con=cnx,
                           if_exists='replace', index=False)
    
    logging.info('******* Checking Column Info df_lead_scoring *********')
    logging.info(df_lead_scoring.columns)
    
    #df_lead_scoring.to_csv('df_new_data_predicted.csv', index=False)
    cnx.close()

###############################################################################
# Define function to map insignificant categorial variables to "others"
###############################################################################
def map_categorical_vars():
    '''
    This function maps all the unsignificant variables present in 'first_platform_c'
    'first_utm_medium_c' and 'first_utm_source_c'. The list of significant variables
    should be stored in a python file in the 'mapping/significant_categorical_level.py' 
    so that it can be imported as a variable in utils file.
    

    INPUTS
        db_file_name : Name of the database file
        db_path : path where the db file should be
        list_platform : list of all the significant platform.
        list_medium : list of all the significat medium
        list_source : list of all the significant source

        **NOTE : list_platform, list_medium & list_source are all constants and
                 must be stored in '/mappings/significant_categorical_level.py'
                 file. The significant levels are calculated by taking top 90
                 percentile of all the levels. For more information refer
                 'data_cleaning.ipynb' notebook.
  

    OUTPUT
        Saves the processed dataframe in the db in a table named
        'categorical_variables_mapped'. If the table with the same name already 
        exists then the function replaces it.

    
    SAMPLE USAGE
        map_categorical_vars()
    '''
    cnx = sqlite3.connect(DB_PATH+DB_FILE_NAME)

    df_lead_scoring = pd.read_sql('select * from city_tier_mapped', cnx)

    new_df = df_lead_scoring[~df_lead_scoring['first_platform_c'].isin(
        list_platform)]
    
    # replace the value of these levels to others
    new_df['first_platform_c'] = "others"
    old_df = df_lead_scoring[df_lead_scoring['first_platform_c'].isin(
        list_platform)]  # get rows for levels which are present in list_platform
    # concatenate new_df and old_df to get the final dataframe
    df = pd.concat([new_df, old_df])

    # get rows for levels which are not present in list_medium
    new_df = df[~df['first_utm_medium_c'].isin(list_medium)]
    # replace the value of these levels to others
    new_df['first_utm_medium_c'] = "others"
    # get rows for levels which are present in list_medium
    old_df = df[df['first_utm_medium_c'].isin(list_medium)]
    # concatenate new_df and old_df to get the final dataframe
    df = pd.concat([new_df, old_df])

    # get rows for levels which are not present in list_source
    new_df = df[~df['first_utm_source_c'].isin(list_source)]
    # replace the value of these levels to others
    new_df['first_utm_source_c'] = "others"
    # get rows for levels which are present in list_source
    old_df = df[df['first_utm_source_c'].isin(list_source)]
    # concatenate new_df and old_df to get the final dataframe
    df = pd.concat([new_df, old_df])

    df = df.drop_duplicates()
    logging.info('******* Checking Column Info  for df *********')
    logging.info(df.columns)
    
    #df.to_csv('categorical_variables_mapped.csv', index=False)
    
    df.to_sql(name='categorical_variables_mapped', con=cnx, if_exists='replace', index=False)
    cnx.close()

##############################################################################
# Define function that maps all the interaction columns into 5 types of interactions
##############################################################################
def interactions_mapping():
    '''
    This function maps the interaction columns into 5 unique interaction columns
    These mappings are present in 'mappings/interaction_mapping.csv' file. 


    INPUTS
        db_file_name : Name of the database file
        db_path : path where the db file should be
        interaction_mapping_file : path to the csv file containing interaction's
                                   mappings
        index_columns : list of columns to be used as index while pivoting and
                        unpivoting
                        
        NOTE : Since while inference we will not have 'app_complete_flag' which is
        our label, we will have to exculde it from our index_columns. It is recommended 
        that you use an if loop and check if 'app_complete_flag' is present in 
        'categorical_variables_mapped' table and if it is present pass a list with 
        'app_complete_flag' in it as index_column else pass a list without 'app_complete_flag'
        in it.
    
    OUTPUT
        Saves the processed dataframe in the db in a table named 
        'interactions_mapped'. If the table with the same name already exists then 
        the function replaces it.
        
        It also drops all the features that are not requried for training model and 
        writes it in a table named 'model_input'

    
    SAMPLE USAGE
        interactions_mapping()

 
    '''
    cnx = sqlite3.connect(DB_PATH+DB_FILE_NAME)

    df = pd.read_sql('select * from categorical_variables_mapped', cnx)
    
    logging.info('printing all categorical_variables_mapped')
    logging.info(df.columns)
    
    if 'app_complete_flag' in df.columns:
        index_variable = INDEX_COLUMNS_TRAINING
    else:
        index_variable = INDEX_COLUMNS_INFERENCE
    
    logging.info(index_variable)
    
    df_event_mapping = pd.read_csv(INTERACTION_MAPPING, index_col=[0])
    logging.info(df_event_mapping.columns)
    
    df_unpivot = pd.melt(df, id_vars=index_variable, var_name='interaction_type', value_name='interaction_value')
    df_unpivot['interaction_value'] = df_unpivot['interaction_value'].fillna(0)
    df = pd.merge(df_unpivot, df_event_mapping,
                  on='interaction_type', how='left')
    df = df.drop(['interaction_type'], axis=1)
    
    df_pivot = df.pivot_table(
        values='interaction_value', index=index_variable, columns='interaction_mapping', aggfunc='sum')
    df_pivot = df_pivot.reset_index()
    
    df_pivot.to_sql(name='interactions_mapped', con=cnx, if_exists='replace', index=False)
    
    df_model_input = df_pivot.drop(NOT_FEATURES, axis=1)
    
    
    logging.info('******* Checking Column Info for df_model_input *********')
    logging.info(df_model_input.columns)
    
    # if need pl write to CSV file to check the data 
    #df_model_input.to_csv('model_input.csv', index=False)
    
    df_model_input.to_sql(name='model_input', con=cnx, if_exists='replace', index=False)
    
    cnx.close()