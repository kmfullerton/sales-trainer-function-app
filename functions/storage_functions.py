import requests 
import queries
import logging
from functions import llm_functions
logger = logging.getLogger()


PWD = 'SeiAtl115'
postgres_uri = 'sales-trainer-postgres.postgres.database.azure.com', 
postgres_port = 5432
postgres_db = 'postgres', 
postgres_user = 'admin01'

def insert_user_input_to_table(user_id, input_text):
    con = queries.uri("sales-trainer-postgres.postgres.database.azure.com", 5432, "postgres", "admin01", PWD)
    query = f"INSERT INTO user_inputs(user_id,  input_text) VALUES ({user_id}, '{input_text}')"
    with queries.Session(con) as session:
        results = session.query(query)
    return results


def insert_llm_response_to_table(user_id, model_output):
    con = queries.uri("sales-trainer-postgres.postgres.database.azure.com", 5432, "postgres", "admin01", PWD)
    query = f"INSERT INTO llm_outputs(user_id,  output_text) VALUES ({user_id}, '{model_output}')"
    with queries.Session(con) as session:
        results = session.query(query)
    return results

def fetch_personas_from_table():
    con = queries.uri("sales-trainer-postgres.postgres.database.azure.com", 5432, "postgres", "admin01", PWD)
    query = f"SELECT persona_id, persona_short_name, persona_description, persona_characteristics, image_file_location FROM personas;"
    with queries.Session(con) as session:
        results = session.query(query)
    return results

def fetch_scenarios_from_table():
    con = queries.uri("sales-trainer-postgres.postgres.database.azure.com", 5432, "postgres", "admin01", PWD)
    query = f"SELECT scenario_id, actor_description, objectives, scenario_short_name, scenario_description, suggested_content FROM scenarios;"
    with queries.Session(con) as session:
        results = session.query(query)
    return results