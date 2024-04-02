import pandas as pd
import seaborn as sns
import numpy as np

from flask import Flask, jsonify, request
import psycopg2 as pg2
import psycopg2.extras
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)


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
    




@app.route("/")
def hello_world():
    return "Hello, World!"

@app.route("/get_ages")
def get_ages():
    conn = get_conn()
    cur = conn.cursor()


    cur.execute("SELECT * FROM az_bb_228_age")
    age_of_serveyed = cur.fetchall()

    conn.close()
    cur.close()


    print(age_of_serveyed)



    return jsonify(age_of_serveyed)


    














  


  
# cur = conn.cursor() 
# conn.commit()
# cur.close() 
# conn.close() 
# print(type(conn))
