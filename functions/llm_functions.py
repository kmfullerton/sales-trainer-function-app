import requests
import pandas as pd
import json
import queries
import logging
logger = logging.getLogger()

URL = 'https://sales-trainer-workspace-wxvzq.eastus2.inference.ml.azure.com/score'
TOKEN = 'Bugamtw1Z6rdNf4K3ldveocbXD5Fm7Nx'
PWD = 'SeiAtl115'

TOP_P = 0.8
TEMPERATURE = 0.8
MAX_TOKENS = 96

def send_single_message(input_text):
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
  
    body = {
      "input_data": {
        "input_string": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"{input_text}"}
            ],
        "parameters": {
            "temperature": TOP_P,
             "top_p": TEMPERATURE,
            "max_new_tokens": MAX_TOKENS
            }
        }
    }
    response = requests.post(url=URL, headers=headers, data=json.dumps(body))
    response_obj = response.json()['output']
    return response_obj

def send_conversation(conversation_json):
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
  
    body = {
      "input_data": {
        "input_string":json.loads(conversation_json),
        "parameters": {
            "temperature": TOP_P,
             "top_p": TEMPERATURE,
            "max_new_tokens": MAX_TOKENS
            }
        }
    }

    response = requests.post(url=URL, headers=headers, data=json.dumps(body))
    response_obj = response.json()
    return response_obj['output']

def format_model_output(text):
    formatted_text = text.replace("'", "''").replace("\n", " ").replace("\r", " ")
    return formatted_text

def get_conversation_context(user_id):
    query = f'''
            SELECT
                'user' AS role,
                input_text AS content,
                timestamp
            FROM
                user_inputs
            WHERE
                user_id = {user_id}
            UNION
            SELECT
                'assistant' AS role,
                output_text AS content,
                timestamp
            FROM
                llm_outputs
            WHERE
                user_id = {user_id}
            ORDER BY
                timestamp'''
    con = queries.uri("sales-trainer-postgres.postgres.database.azure.com", 5432, "postgres", "admin01", PWD)
    with queries.Session(con) as session:
       results = session.query(query)
       output = results.items()
    df = pd.DataFrame.from_records(output)
    df.drop(columns=['timestamp'], inplace=True)
    conversation_obj = df.to_json(orient='records')
    return conversation_obj