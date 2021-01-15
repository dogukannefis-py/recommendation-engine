from recommendationES import searchEs,sellerBatchEs    ## import our functions
import elasticsearch
from elasticsearch import Elasticsearch
import pandas as pd
from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)  
app.config['SECRET_KEY'] = 'you-!will-!never-!guess!'
es_client = Elasticsearch(hosts="http://localhost:9699/",timeout=500)


@app.route('/api/browsing_history', methods=['GET'])
def get_history():

    if 'user-id' in request.args:
        userid = str(request.args['user-id'])
    else:
        return "Error: User id field provided. Please specify an id."
    
    index="historybrowsing"
    try:
        df=searchEs(es_client,userid,index)
        products=df['product'].to_list()
    except:
        return "Error: User id field is uncorrect"
    
    if len(products)<6:
        products=[]
        
    data = {
        "user-id":userid,
        "products":products,
        "type":"personalized"
    }

    return jsonify(data)


@app.route('/api/recommendation', methods=['GET'])
def get_recommendation():
    
    if 'user-id' in request.args:
        userid = str(request.args['user-id'])
    else:
        return "Error: No id field provided. Please specify an id."
    
    index="historybrowsing"
    strategy="second"
    typ="non-personalized"
    products=[]
    
    try:
        df=searchEs(es_client,userid,index)
        products=df['product'].to_list()
        strategy="first"
        category_list=df.category.value_counts().head(3).index.to_list()  ## Get most 3 category
        typ="personalized"
    except: 
        category_list=[]
        strategy="second"

  
    index="sellerbatch*"
    dfSeller=sellerBatchEs(es_client,index,category_list,strategy)
    products=dfSeller['product'].to_list()
    if len(products)<6:
        products=[]
    
    
    data = {
        "user-id":userid,
        "products":products,
        "type":typ
    }

    return jsonify(data)


@app.route('/api/insert_data', methods=['POST'])
def insert_data():
    
    if not request.json or not 'product-id' in request.json or not 'user-id' in request.json:
        abort(400)
  
    product = request.json['product-id']
    userid = request.json['user-id']
    timestamp=round(datetime.now().timestamp(),3)
    
    body = {
         'userid': userid,
        'product': product,
        'timestamp': timestamp
    }

    result = es_client.index(index='historybrowsing', id=int(timestamp)+100000, body=body)

    return jsonify(result)


@app.route('/api/delete_data', methods=['POST'])
def delete_data():
    
    if not request.json or not 'product-id' in request.json or not 'user-id' in request.json :
        abort(400)
  
    product = request.json['product-id']
    userid = request.json['user-id']
    
    query_body = {
      "query": {
        "bool": {    
         "must":[
                    {
                      "match": {
                        "userid": "-"+userid.split("-")[1]
                      }
                    },
                    {
                      "match": {
                        "product": "-"+product.split("-")[1]
                      }
                    }
                        
                  ]
                }
              }
        }
    
    

    result=es_client.delete_by_query(index='historybrow*', body=query_body)

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port='4340',threaded=True)