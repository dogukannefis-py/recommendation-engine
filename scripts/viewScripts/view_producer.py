#!/usr/bin/env python3
import json
from time import sleep
from json import dumps
from kafka import KafkaProducer
from datetime import datetime

 #load json and create model
productViewPath='./scripts/viewScripts/product-views.json'

productViewList=[]

with open(productViewPath, 'r') as f:
    for jsonObj in f:
        productViewDict = json.loads(jsonObj)  ##Json object to dict
        productViewList.append(productViewDict)

## Kafka Producer
producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
                         value_serializer=lambda x: dumps(x).encode('utf-8'))

## Publish data wirh 1 second interval
for product_view in productViewList:
    product_view['timestamp']=round(datetime.now().timestamp(),3)
    producer.send('productView', value=product_view)
    sleep(1)

