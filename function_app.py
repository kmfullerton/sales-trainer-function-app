import azure.functions as func
import logging
import requests
import queries
import pandas as pd
from functions import llm_functions, storage_functions
import logging
logger = logging.getLogger()

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

def format_text_for_postgres(text):
    formatted_text = text.replace("'", "''").replace("\n", " ").replace("\r", " ").replace("\'", "'")
    return formatted_text

@app.function_name("MainTrigger")
@app.route(route="main")
def http_trigger_to_postgres(req: func.HttpRequest) -> func.HttpResponse:
    logger.info('Python HTTP trigger function processed a request.')

    user_id = req.params.get('user_id')
    input_text = req.params.get('input_text')
    if not user_id:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            user_id = req_body.get('user_id')
    if not input_text:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            input_text = req_body.get('input_text')

    logging.info(f"Inserting row: {user_id}, {input_text}")
    if user_id:
        logger.info(f"Writing row to user input table: {user_id}, {input_text}")
        formatted_input_text = format_text_for_postgres(input_text)
        input_results = storage_functions.insert_user_input_to_table(user_id=user_id, input_text=formatted_input_text)
        
        logger.info(f"Fetching conversation history for user id {user_id}")
        conversation = llm_functions.get_conversation_context(user_id)
        logger.info(f"Sending conversation to LLM.")
        response = llm_functions.send_conversation(conversation)

        logger.info("Formatting Model response.")
        text_to_insert = format_text_for_postgres(response)
        logger.info("Writing model response to table.")
        output_results = storage_functions.insert_llm_response_to_table(user_id, text_to_insert)
        return func.HttpResponse(f"{output_results}.")
    else:
        return func.HttpResponse( 
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
    
@app.function_name("ScoringTrigger")
@app.route(route="scoring")
def scoring_function(req: func.HttpRequest) -> func.HttpResponse:
    logger.info('Python Scoring HTTP trigger function processed a request.')
    pass

@app.function_name("GetPublicPersonas")
@app.route(route="getPersonas")
def get_personas(req: func.HttpRequest) -> func.HttpResponse:
    personas = storage_functions.fetch_personas_from_table()
    logger.info(f"Personas returned: {personas}")
    return func.HttpResponse(f"{personas}.")

@app.function_name("GetPublicScenarios")
@app.route(route="getScenarios")
def get_scenarios(req: func.HttpRequest) -> func.HttpResponse:
    scenarios = storage_functions.fetch_scenarios_from_table()
    logger.info(f"Scenarios returned: {scenarios}")
    return func.HttpResponse(f"{scenarios}.")