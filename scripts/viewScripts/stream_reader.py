#!/usr/bin/env python3
from kafka import KafkaConsumer
from json import loads
from elasticsearch import Elasticsearch,helpers
from time import sleep

## Elasticsearch Connection
es = Elasticsearch(hosts="http://localhost:9699/",timeout=50) 

## Subscribe a topic "productViews" 
consumer = KafkaConsumer(
    'productView',
     bootstrap_servers=['localhost:9092'], ## bootstrap server
     auto_offset_reset='earliest',   ##from beginning
     enable_auto_commit=True,
     group_id='my-group',
     value_deserializer=lambda x: loads(x.decode('utf-8')))


## message to ES
for message in consumer:
    message = message.value
    
    userid=message['userid']
    productid=message['properties']['productid']
    timestamp=message['timestamp']
    
    data={
                "userid":userid,
                "product":productid,
                "timestamp":timestamp
            }

    res = es.index(index='historybrowsing',id=int(timestamp)+100,body=data) ## send json the index "browsinghistory"
