import azure.functions as func
import logging
import requests
import queries
import pandas as pd
PWD = 'SeiAtl115'
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

    
@app.route(route="http_trigger")
def http_trigger_to_postgres(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    user_id = req.params.get('user_id')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')
    if not user_id:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            user_id = req_body.get('user_id')


    if name & user_id:
        con = queries.uri("sales-trainer-postgres.postgres.database.azure.com", 5432, "postgres", "admin01", PWD)
        query = f'INSERT INTO demo-app (id, name) VALUES ({user_id}, {name})'
        with queries.Session(con) as session:
            results = session.query(query)

        return func.HttpResponse(f"Hello, {name}. {results}.")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )