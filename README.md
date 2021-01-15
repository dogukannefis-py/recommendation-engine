# Recommendation-Engine
##### Build batch and real-time data pipelines together with high-performance rest APIs to create a real-time recommendation engine. (e-commerce)

### Directory Tree `

    |— docker-compose.yml

    |— scripts

         |— modules.sh

         |— ETL

            |— extract_batch.py

            |— update_category.py

    |— viewScripts

            |— product-views.json

            |— view_producer.py

            |— stream_reader.py

    |— API

           |— api.py

           |— recommendationES.py`
           
           
### **CUSTOM TECHONOLOGIES**

**Elasticsearch:** For write operations, Elasticsearch is utilized. Custom mapping is not created, because Elasticsearch create mapping and schema from json data. Elasticsearch is NoSql. It is easy to work with JSON.  In a few cases, such as category update on productViews index, update operastion is used.

**Python:** For script language, View Producer App, Stream Reader App and ETL Process, python is selected. In some necesearry Python Modules are required to run Python Scripts. These  (modeules.sh) will be installed after docker up. 

**REST API:** For REST API, python(Flask library)  is used. Flask is web framework and extensible in APIs.

**Postman:** Postman is used to test REST API.

**Kafka:**  it is user for messaging queue and short-time data store.

**PostgreSQL:** Products, orders and order_items tables

**Zookeeper:** It is required for Kafka to run



### System Architecture
![System Architecture](https://github.com/dogukannefis-py/recommendation-engine/blob/main/images/Data%20Flow%20Diagram%20(Logical)%20Example.png)
  
  
### **Scripts:**

**view_producer.py ⇒** read "prdouct-views.json"and publish one event in a second to Kafka. The current timestamp was added to product view event data. (**topic:** productView)

**stream_reader.py ⇒** read **"productView"** topic from kafka and writes this json to Elasticsearch. 

( Elasticsearch index: **historybrowsing**)

**extract_batch.py ⇒**  read batch data from PostgreSQL, create category based and general best sellers flow(top ten products of this category bought (last month) by the most distinct users ) and writes to Elasticsearch.

**update_category.py ⇒**  read product_id and category_id from products table from PostgreSQL and update category column of productView index in Elasticsearch

**api.py ⇒**  a recommendation Rest API to provide given endpoints.  It is explained in detail "REST API TEST" section.

**recommendationES.py ⇒** includes functions are specific for api.py
 
 
 
 ### INSTALLATION
 `docker-compose -f ./docker-compose.yml up -d &`
#### After setup is completed: (Docker-compose up) 
- Kafka port: **9092**
- Elasticsearch: **9699**
- Kibana: **5601**
- PostgreSQL port: **5432**

     ⇒ **Username:** postgres
     
     ⇒ **Password:** 123456
     
 necessary python modules installed

```python
 sh ./scripts/modules.sh
```

 view_producer.py is running and publish data to Kafka (**topic:** productView)
 ```python
nohup python3 -u ./scripts/viewScripts/view_producer.py > prod_out.log &
```

read "productView" topic from kafka and writes this json to Elasticsearch. 
 ```python
nohup python3 -u ./scripts/viewScripts/stream_reader.py > cons_out.log &
 ```
 
 read batch data from PostgreSQL, create category based and general best sellers flow and writes to Elasticsearch. (top ten products of this category bought (last month) by the most distinct users )
  ```python
 python3 ./scripts/ETL/extract_batch.py
  ```
  
  read product_id and category_id from products table from PostgreSQL and update category column of productView index in Elasticsearch
  ```python
 python3  ./scripts/ETL/update_category.py
  ```
  
  a recommendation Rest API to provide given endpoints.  
    ```python
  python3 -u ./API/api.py
    ```
    
### **ELASTICSEARCH MAPPING**

**Index:  historybrowsing**

```json
{
  "mapping": {
    "properties": {
      "category": {
        "type": "text",
        "fields": {
          "keyword": {
            "type": "keyword",
            "ignore_above": 256
          }
        }
      },
      "product": {
        "type": "text",
        "fields": {
          "keyword": {
            "type": "keyword",
            "ignore_above": 256
          }
        }
      },
      "timestamp": {
        "type": "float"
      },
      "userid": {
        "type": "text",
        "fields": {
          "keyword": {
            "type": "keyword",
            "ignore_above": 256
          }
        }
      }
    }
  }
}
```

**Index: sellerbatch**

```json
{
  "mapping": {
    "properties": {
      "category": {
        "type": "text",
        "fields": {
          "keyword": {
            "type": "keyword",
            "ignore_above": 256
          }
        }
      },
      "count": {
        "type": "long"
      },
      "product": {
        "type": "text",
        "fields": {
          "keyword": {
            "type": "keyword",
            "ignore_above": 256
          }
        }
      },
      "rank": {
        "type": "long"
      }
    }
  }
}
```

## REST API

### **Browsing History**
⇒ return the last ten products viewed by a given user and sorted by view date.
```python
localhost:4340/api/browsing_history?user-id=<userid>
```

##### **INSERT**
⇒ users which they can insert a product from their history
```python
localhost:4340/api/inser_data
```
##### **DELETE**
```python
=> users which they can delete a product from their history
localhost:4340/api/delete_data
```

### **RECOMMENDATION**
⇒ Offer ten products based on most three categories.

⇒ or top ten products bought (last month) by the most distinct users without any filter. (if user-id is not found)
```python
localhost:4340/api/recommendation?user-id=<userid>
```


