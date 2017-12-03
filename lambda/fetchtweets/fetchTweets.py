from __future__ import print_function
from pprint import pprint
import boto3
import json
from elasticsearch import Elasticsearch, RequestsHttpConnection
import urllib

from datetime import datetime
# from requests_aws4auth import AWS4Auth

def connectES(esEndPoint):
    print ('Connecting to the ES Endpoint {0}'.format(esEndPoint))
    try:
        esClient = Elasticsearch(
            hosts=[{'host': esEndPoint, 'port': 443}],
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection)
        return esClient
    except Exception as E:
        print("Unable to connect to {0}".format(esEndPoint))
        print(E)
        exit(3)

# def search(keyword):

#         data = {
#             "size": 2000,
#             "query": {
#                 "query_string": { "query": keyword }
#             }
#         }
#         search_address = 'http://search-tweets2-aky5stilg35q3ivtphzonukb3q.us-west-2.es.amazonaws.com/tweetindex/tweet/_search'
#         response = requests.post(search_address, data=json.dumps(data))

#         return response.json()

def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    esClient = connectES("search-tweets2-aky5stilg35q3ivtphzonukb3q.us-west-2.es.amazonaws.com")
    res = esClient.search(index="tweetindex", body={
    	"query": {
    		"bool": {
    			"must": [
    			    { "range": {"timestamp" :{"gte" : event['time']}}},
    				{"query_string": {"query": event['keyword'] }}
    			]
    		}
    	}
    })
    print("Got %d Hits:" % res['hits']['total'])

    ls = {}
    ls["tweet"] = []

    for hit in res['hits']['hits']:
        ls["tweet"].append((hit["_source"]))
        
    return ls