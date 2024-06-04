import pandas as pd
import seaborn as sns
import numpy as np

from flask import Flask, jsonify, request
import psycopg2 as pg2
import psycopg2.extras
from dotenv import load_dotenv
import os

from authlib.integrations.flask_oauth2 import ResourceProtector
from validator import Auth0JWTBearerTokenValidator

load_dotenv()
app = Flask(__name__)


require_auth = ResourceProtector()
validator = Auth0JWTBearerTokenValidator(
    os.getenv('DOMAIN'),
    os.getenv('AUDIENCE')
)
require_auth.register_token_validator(validator)



DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')


# If any database environment variables is not set, raise an error
if DB_NAME is None:
    raise ValueError('DB_NAME is not set')
elif DB_USER is None:
    raise ValueError('DB_USERNAME is not set')
elif DB_PASSWORD is None:
    raise ValueError('DB_PASSWORD is not set')
elif DB_HOST is None:
    raise ValueError('DB_HOST is not set')


def get_conn():
    conn = pg2.connect(database=DB_NAME,  
                        user=DB_USER, 
                        password=DB_PASSWORD,  
                        host=DB_HOST, 
                        port="5432", 
                        cursor_factory = pg2.extras.RealDictCursor)
    
    return conn
    

@app.route("/get_ages")
@require_auth(None)
def get_ages():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM az_bb_228_age")
    age_of_serveyed = cur.fetchall()
    conn.close()
    cur.close()

    return jsonify(age_of_serveyed)

    
@app.route("/get_area_codes")
def get_area_codes():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM az_bb_228_area_code")
    ac_of_surveyed = cur.fetchall()
    conn.close()
    cur.close()

    return jsonify(ac_of_surveyed)


def create_table(table_name):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
            f"""CREATE TABLE IF NOT EXISTS public.{table_name}  (name text, email text, dob text, phone text, timestamp text);
                    """)
    
    conn.commit()
    conn.close()
    cur.close()


# play around with the Auth0, pretend that you are another website
# Try and launch API for EC2 and have api website associated with it - based on tutorial
@app.route('/insert_event_response', methods=['POST'])
@require_auth("write:sweepstake_response")
def insert_sweepstake_response():
    if request.is_json: # header must be "Content-Type: application/json"
        body = request.get_json()
        #%100000 a better way to do this. Too many thigns to learn
        body_elements = {'event':None, 
                         'timestamp':None, 
                         'day':None,
                         'month':None, 
                         'year':None, 
                         'name':None, 
                         'email':None, 
                         'dob':None, 
                         'phone':None}
        for element in body_elements:
            if element not in body.keys():
                return {"message": f'{element} is required for request'}, 400
            else:
                body_elements[element] = body.get(element)
        
        table_name = f"{body_elements['event']}_{body_elements['month']}_{body_elements['year']}"
        create_table(table_name)


        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            f"""INSERT INTO {table_name} (name, email, dob, phone, timestamp)
                VALUES ('{body_elements['name']}', '{body_elements['email']}', '{body_elements['dob']}', '{body_elements['phone']}', '{body_elements['timestamp']}');
                    """)
        conn.commit()
        conn.close()
        cur.close()

        return {"message": "Successful insert"}, 200

    else:
        return {'message': 'request body must be JSON'}, 400

        

        

        




