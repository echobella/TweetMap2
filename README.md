# TweetMap2

Architecture: 

3 lambda functions:
  1. tweet streaming + SQS + sentiment analysis + SNS
  2. index processed tweets into ElasticSearch
  3. fetch tweets from ElasticSearch

Front end triggering the fetching from ES based on a keyword
