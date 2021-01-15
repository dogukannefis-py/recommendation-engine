#!/usr/bin/env python3
import psycopg2
import pandas as pd
from elasticsearch import Elasticsearch
from elasticsearch import helpers
import time

def update_category(es,product,category):

    """
    Update category for product => index="browsinghistory" - Elasticsearch
    """

    q = {
     "script": {
        "lang": "painless",
        "inline": "ctx._source.category=params.newsupp",
        "params":{
                 "newsupp":category
          }
     },
     "query": {
        "match":{
            "product":product
        }
     }
    }

    es.update_by_query(body=q, index='historybrow*')



# Update connection string information
host = "localhost"
dbname = "data-db"
user = "postgres"
password = 123456
port="25060"

# Construct connection string
conn_string = "host={0} user={1} dbname={2} password={3}".format(host, user, dbname, password)
conn = psycopg2.connect(conn_string)
print("Connection established")

cur = conn.cursor()

query_sql2 = """
            SELECT * FROM products
            """

cur.execute(query_sql2)
# get a list of tupples
tupples = cur.fetchall()
cur.close()

column_names=['product_id','category_id']
# turn it into a pandas dataframe
df = pd.DataFrame(tupples, columns=column_names)

## ES Client Connection
es_client = Elasticsearch(hosts="http://localhost:9699/",timeout=50)

for prod,category in tupples:
    product="-"+prod.split("-")[1]
    update_category(es_client,product,category)
