import elasticsearch
from elasticsearch import Elasticsearch
import pandas as pd

def searchEs(es,userid,index):
    query_body = {
      "query": {
        "bool": {
          "must": {
            "match": {      
              "userid": "-"+userid.split("-")[1]
            }
          }
        }
      }
    }


    res=es.search(index=index,body=query_body) #size=row sayısı
    #Query results to the dataframe
    results=[]
    for hit in res['hits']['hits']:
        result=hit['_source']
        results.append(result)

    df=pd.DataFrame(results)
    try:
        df.sort_values(by='timestamp', ascending=False,inplace=True)   ## Sort by timestamp
    except:
        print("User-id not found")
        
    return df



def sellerBatchEs(es,index,category_list,strategy="second"):
    """
    Explanation
    """
    
    if strategy=="first":
        query_body = {
          "query": {
            "bool": {    
             "must": {
              "bool": {
                  "should": [
                        {
                          "match": {
                            "category":category_list[0]
                          }
                        },
                        {
                          "match": {
                            "category": category_list[1]
                          }
                        },
                        {
                          "match": {
                            "category": category_list[2]
                          }
                        }

                      ]
                    }
                  }
            }
        }
        }
        
        
        res=es.search(index=index,body=query_body) 
    
    else:
        query_second={
            "query": {
                "match_all":{

                }
            }
        }
        
        res=es.search(index=index,body=query_second,size=10)  ## if strategy="second" return top 10 of all category
        
    #Query results to the dataframe
    results=[]
    for hit in res['hits']['hits']:
        result=hit['_source']
        results.append(result)

    df=pd.DataFrame(results)
   
    return df