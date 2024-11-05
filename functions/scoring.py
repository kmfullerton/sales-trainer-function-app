import argparse

import os
import logging
import json
import uuid
import queries
import pandas as pd
import datetime


logger = logging.getLogger()



def collect_only_role_words(conversation_obj: object, role: str)-> str:
    logger.info(f"Selecting words from {role}.")
    role_words = ''
    for ind, obj in conversation_obj.iterrows():
        if obj['role'] == role:
            role_words += ' ' + obj['content']
    return role_words


def collapse_json_to_single_string(conversation_obj:object)-> str:
    logger.info('Converting conversation dataframe to a paragraph.')
    lines = ''
    for ind, row in conversation_obj.iterrows():
        role = row['role']
        content = row['content']
        line = f'{role}: {content}, '
        lines = lines  + line
    return lines 


def calc_filler_words_score(user_words: str) -> float:
    filler_words = ['like', 'well', 'actually', 'right', 'literally', 'seriously', 'so', 'okay', 'basically', 'yeah', 'totally', 'um', 'just', 'er'] 
    logger.info(f"Calculating the prevalence of these filler words: {filler_words}")
    filler_counter = 0
    for word in filler_words:
        counter = user_words.lower().split().count(word)
        filler_counter += counter
        divisor = len(user_words.lower().split())
        if divisor != 0:
            filler_score = 1-(filler_counter/divisor)
        else:
            filler_score = 1
    return filler_score
    
def calc_avg_wpm(conversation_obj:object)-> float:
    logger.info("Calculating the average WPM spoken by the user.")
    wpm_records = []
    for ind, obj in conversation_obj.iterrows():
        if obj['role'] == 'user':
            text = obj['content']
            word_count = len(text.split())
            time = obj['duration']/10000000 # converts time to seconds
            wpm = 60*word_count/time
            wpm_records.append(wpm)
    divisor = len(wpm_records)
    if divisor != 0:
        avg_wpm = sum(wpm_records)/divisor
    else:
        avg_wpm = 0
    return avg_wpm

## Conversational Balance
def calc_balance_score(conversation_obj:object)->float:
    logger.info("Calculating the conversational balance between the model and user.")
    user_words = collect_only_role_words(conversation_obj, 'user')
    model_words = collect_only_role_words(conversation_obj, 'assistant')
    divisor = len(user_words.split())
    if divisor == 0:
        balance_score = 0
    else:
        balance_score = len(model_words.split())/divisor
    return balance_score

## Average Response Time
def calc_avg_response_time(conversation_obj: object)-> float:
    logger.info('Calculating the average response time of the user across the full conversation.')
    response_time_total = 0
    response_count = 0
    for index, row in conversation_obj.iterrows():
        if index > 0:
            prev_row = conversation_obj.iloc[index-1]
            response_time = datetime.datetime.fromisoformat(row['timestamp']) - datetime.datetime.fromisoformat(prev_row['timestamp'])
            if row['role'] == 'user':
                response_count += 1
                response_time_total += response_time.total_seconds()
    divisor = (1000*response_count)
    if divisor == 0:
        response_time_score = 0
    else:
        response_time_score = response_time_total/divisor
    return response_time_score

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
    return df

def score_conversation(user_id):
    conversation_obj = get_conversation_context(user_id)

    print(f"Conversation retrieved with {len(conversation_obj)} lines.")
    user_words = collect_only_role_words(conversation_obj, 'user')
    lines = collapse_json_to_single_string(conversation_obj)
    print('Calculating quantitative score components.')
    filler_score = calc_filler_words_score(user_words)
    pacing_score = calc_avg_wpm(conversation_obj)
    balance_score = calc_balance_score(conversation_obj)
    response_time_score = calc_avg_response_time(conversation_obj)
    print(f"Filler score: {filler_score}")
    print(f"Pacing score: {pacing_score}")
    print(f"Balance score: {balance_score}")
    print(f"Response Time score: {response_time_score}")

    json_dict = {
        "filler": filler_score,
        "pacing": pacing_score,
        "balance": balance_score,
        "response_time": response_time_score
    }
    return json_dict
