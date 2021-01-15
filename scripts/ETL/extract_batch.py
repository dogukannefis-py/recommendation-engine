#!/usr/bin/env python3
import psycopg2
import pandas as pd
from elasticsearch import Elasticsearch
from elasticsearch import helpers
import time


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

query_sql = """
            with t1 as(
            SELECT category,product,COUNT(DISTINCT user_id),
                 ROW_NUMBER() OVER(PARTITION BY category ORDER BY COUNT(DISTINCT user_id) DESC) AS Rank
            FROM (SELECT p.product_id AS product,p.category_id AS category,user_id
                FROM products AS p 
                  INNER JOIN order_items AS o 
                    ON p.product_id=o.product_id
                  INNER JOIN orders
                    ON o.order_id=orders.order_id
                ) AS t1
            GROUP BY category,product
            ORDER BY COUNT(DISTINCT user_id) DESC
            )
            SELECT *
            FROM t1
            WHERE rank<11
            """

cur.execute(query_sql)


# Naturally we get a list of tupples
tupples = cur.fetchall()
cur.close()

column_names=['category','product','count','rank']
# turn it into a pandas dataframe
df = pd.DataFrame(tupples, columns=column_names)


## ----------------------------------------------------------
## ----------------------------------------------------------

##Send data to ES

es_client = Elasticsearch(hosts="http://localhost:9699/",timeout=50)

def doc_generator(df):
    df_iter = df.iterrows()
    for index, document in df_iter:
        yield {
                "_index": 'sellerbatch',
                "_type": "_doc",
                "_id" : index,
                "_source": document.to_dict(),
            }
    raise StopIteration
    
helpers.bulk(es_client, doc_generator(df))
