import pandas as pd
import seaborn as sns
import numpy as np

from flask import Flask, jsonify, request
import psycopg2 as pg2
import psycopg2.extras
from dotenv import load_dotenv

import os
from datetime import datetime, timezone

from authlib.integrations.flask_oauth2 import ResourceProtector
from werkzeug.middleware.proxy_fix import ProxyFix

load_dotenv()
app = Flask(__name__)

#require_auth = ResourceProtector()
#validator = Auth0JWTBearerTokenValidator(
#    os.getenv('DOMAIN'),
#    os.getenv('AUDIENCE')
#)
#require_auth.register_token_validator(validator)

app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)



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
#@require_auth(None)
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



# play around with the Auth0, pretend that you are another website
# Try and launch API for EC2 and have api website associated with it - based on tutorial
@app.route('/insert_event_response', methods=['POST'])
#@require_auth("write:sweepstake_response")
def insert_sweepstake_response():
    if request.is_json: # header must be "Content-Type: application/json"
        body = request.get_json()
        #%100000 a better way to do this. Too many thigns to learn
        body_elements = {'name':None, 
                         'email':None, 
                         "phone_number":None, 
                         'date_of_birth':None, 
                         'event_name':None}
        
        for element in body_elements:
            if element not in body.keys():
                return {"message": f'{element} is required for request'}, 400

        

        dt = datetime.now(timezone.utc)

        conn = get_conn()
        cur = conn.cursor()
        print(f"""INSERT INTO swingcityyouth (name, email, phone_number, date_of_birth, event_name, timestamp)
                VALUES ('{body['name']}', '{body['email']}', '{body['phone_number']}', '{body['date_of_birth']}', '{body['event_name']}', '{dt}');
                    """)
        cur.execute(
            f"""INSERT INTO swingcityyouth (name, email, phone_number, date_of_birth, event_name, timestamp)
                VALUES ('{body['name']}', '{body['email']}', '{body['phone_number']}', '{body['date_of_birth']}', '{body['event_name']}', '{dt}');
                    """)
        conn.commit()
        conn.close()
        cur.close()

        return {"message": "Successful insert"}, 200

    else:
        return {'message': 'request body must be JSON'}, 400

        

if __name__ == '__main__':
    app.run(debug=True)

