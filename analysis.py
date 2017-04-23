#!/usr/bin/python

import sys
import json
import pandas as pd

try:
    # We open the file 
    tweets_data_path = sys.argv[1]
    tweets_data = []
    tweets_file = open(tweets_data_path, "r")
    
    # We read each line of the file and recover the json
    for line in tweets_file:
        try:
            tweet = json.loads(line)
            tweets_data.append(tweet)    
        except:
            continue
    
    # Print the number of rows         
    print len(tweets_data)
    
    # Transform the Jsoon data in a DataFrame
    tweets = pd.DataFrame()
    tweets['id'] = map(lambda tweet: tweet['id_str'], tweets_data)
    tweets['name'] = map(lambda tweet: tweet['user']['screen_name'], tweets_data)
    tweets['location'] = map(lambda tweet: tweet['user']['location'], tweets_data)
    tweets['date'] = map(lambda tweet: tweet['created_at'], tweets_data)
    tweets['time_zone'] = map(lambda tweet: tweet['user']['time_zone'], tweets_data)
    tweets['retweet_count'] = map(lambda tweet: tweet['retweet_count'], tweets_data)
    tweets['followers_count'] = map(lambda tweet: tweet['user']['followers_count'], tweets_data)
    tweets['urls'] =  map(lambda tweet: tweet['entities']['urls'], tweets_data)
    tweets['text'] = map(lambda tweet: tweet['text'], tweets_data)
    tweets['lang'] = map(lambda tweet: tweet['lang'], tweets_data)
    tweets['country'] = map(lambda tweet: tweet['place']['country'] if tweet['place'] != None else None, tweets_data)
	
    # Print the tweets
    for index, row in tweets.iterrows():
        print(row)
except IndexError:
    print 'No txt file added'
    sys.exit(2)
except IOError as e:
    print "I/O error({0}): {1}".format(e.errno, e.strerror)
except:
    print "Unexpected error:", sys.exc_info()[0]
    sys.exit(2)