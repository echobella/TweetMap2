from django.http import HttpResponse
from django.shortcuts import render
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import time
import json
from elasticsearch import Elasticsearch
import elasticsearch
from requests_aws4auth import AWS4Auth
import time
import geocoder
from django.views.decorators.csrf import csrf_protect, csrf_exempt
import urllib3
# Create your views here.

host = 'search-tweets2-aky5stilg35q3ivtphzonukb3q.us-west-2.es.amazonaws.com' #Creata a domain on ElasticSearch Service and add the endpoint here
awsauth = AWS4Auth('', '', 'us-west-2', 'es')
es = elasticsearch.Elasticsearch(
    hosts=[{'host': host, 'port': 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=elasticsearch.connection.RequestsHttpConnection
)

def index(request):
    return render(request,"home.html",{})

@csrf_exempt
def notifications(request):
    body = json.loads(request.body.decode("utf-8"))
    print(type(body))
    hdr = body['Type']

    if hdr == 'SubscriptionConfirmation':
        url = body['SubscribeURL']
        print("Subscription Confirmation - Visiting URL : " + url)
        http = urllib3.PoolManager()
        r = http.request('GET', url)
        print(r.status)

    if hdr == 'Notification':
        print("SNS Notification")
        tweet = (body['Message'])
        es.index(index='tweetmap', doc_type='tweets',  body=tweet)
    return HttpResponse(status=200)

@csrf_protect
def home(request):
    # import twitter keys and tokens
    # ckey = "consumer api key"
    # csecret = "consumer secret"
    # atoken = "access token"
    # asecret = "access secret"

    # create instance of elasticsearch


    # class TweetStreamListener(StreamListener):
    #     def __init__(self, time_limit=10):
    #         self.start_time = time.time()
    #         self.limit = time_limit
    #
    #     # on success
    #     def on_data(self, data):
    #         # decode json
    #         dict_data = json.loads(data)
    #
    #         if (time.time() - self.start_time) < self.limit:
    #             if 'user' in dict_data and dict_data['user']['location']:
    #                 try:
    #                     doc = {"author": dict_data["user"]["screen_name"],
    #                            "date": dict_data["created_at"],
    #                            "location": {
    #                                 "name": dict_data['user']['location'],
    #                                 "coords": {
    #                                     "lat": geocoder.google(dict_data['user']['location']).latlng[0],
    #                                     "lon": geocoder.google(dict_data['user']['location']).latlng[1]
    #                                 }
    #                             },
    #                            "message": dict_data["text"],
    #                            "my_id": query}
    #                     es.index(index="tweetmap",doc_type="tweets",body=doc)
    #                 except:
    #                     pass
    #                 return True
    #         else:
    #             return False
    #
    #     # on failure
    #     def on_error(self, status):
    #         print(status)
    #
    # # create instance of the tweepy tweet stream listener
    # listener = TweetStreamListener()
    # # set twitter keys/tokens
    # auth = OAuthHandler(ckey, csecret)
    # auth.set_access_token(atoken, asecret)
    # # create instance of the tweepy stream
    # stream = Stream(auth, listener)
    query = str(request.POST.get('myword'))
    # stream.timeout = 10
    # try:
    #     stream.filter(track=[query,'#'+query])
    # except:
    #     pass
    pass_list = {}
    pass_list.setdefault('tweet', [])
    res = es.search(size=1000, index="tweetmap", doc_type="tweets", body={
        "query":{
            "match": {
                "my_id": query
            }
        }
    })
    for j in res['hits']['hits']:
        pass_list['tweet'].append(j['_source'])
    pass_list_final = json.dumps(pass_list)
    return render(request,"index.html",{"my_data":pass_list_final})

def geodist(request, *args, **kwargs):
    # create instance of elasticsearch
    host = 'search-tweets2-aky5stilg35q3ivtphzonukb3q.us-west-2.es.amazonaws.com' #Creata a domain on ElasticSearch Service and add the endpoint here
    awsauth = AWS4Auth('', '', 'us-west-2', 'es')
    es = elasticsearch.Elasticsearch(
        hosts=[{'host': host, 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=elasticsearch.connection.RequestsHttpConnection
    )
    pass_list = {}
    pass_list.setdefault('tweet', [])
    res = es.search(size=1000, index="tweetmap", doc_type="tweets", body={
        "query": {
            "bool": {
                "must": {
                    "match_all": {}
                },
                "filter": {
                    "geo_distance": {
                        "distance": "500mi",
                        "location.coords": {
                            "lat": kwargs["lat"],
                            "lon": kwargs["lng"]
                        }
                    }
                }
            }
        }
    })
    for j in res['hits']['hits']:
        pass_list['tweet'].append(j['_source'])
    pass_list_final = json.dumps(pass_list)
    return render(request,"index.html",{"my_data":pass_list_final})
