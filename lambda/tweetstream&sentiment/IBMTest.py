from watson_developer_cloud import NaturalLanguageUnderstandingV1
from watson_developer_cloud.natural_language_understanding_v1 import Features, SentimentOptions


natural_language_understanding = NaturalLanguageUnderstandingV1(
              username = "7e35fe4b-f501-485d-85bf-e9bdee52f7d0",
              password = "SHWH1ChKlVpI",
              version = "2017-02-27")
response = natural_language_understanding.analyze(
                  text= "It should work now man!",
                  features= Features(sentiment=SentimentOptions())
                  )
print response
score = response["sentiment"]["document"]["score"]
label = response["sentiment"]["document"]["label"]
# print "score:" + score