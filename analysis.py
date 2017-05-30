#!/usr/bin/python

import os
import sys
import json
import pandas as pd
from collections import Counter

UNK = "<UNK>"

def read_tweets_data(file_name):
    tweets_data = []
    tweets_file = open(file_name, "r")

    # We read each line of the file and recover the json
    for line in tweets_file:
        try:
            tweet = json.loads(line)
            tweets_data.append(tweet)
        except:
            continue

    # Print the number of rows
    print len(tweets_data)

    cleaned_tweets_data = {'id': [], 'name': [], 'location': [], 'date': [], 'time_zone': [],
                           'retweet_count': [], 'followers_count': [], 'urls': [], 'text': [],
                           'lang': [], 'country': [], "retweeted_status_id_str": [],
                           "retweeted_status_user_id_str": [],
                           "in_reply_to_user_id_str": [], "in_reply_to_status_id_str": []}

    # Sometimes there could be missing data, if the data is id, discard the entry. Otherwise mark it as None.
    for tweet in tweets_data:
        if 'id_str' not in tweet:
            # This is the reason I'm using a for loop instead of a map.
            continue
        cleaned_tweets_data['id'].append(tweet['id_str'])
        cleaned_tweets_data['name'].append(tweet['user']['screen_name'])
        cleaned_tweets_data['location'].append(tweet['user']['location'])
        cleaned_tweets_data['date'].append(tweet['created_at'])
        cleaned_tweets_data['time_zone'].append(tweet['user']['time_zone'])
        cleaned_tweets_data['retweet_count'].append(tweet['retweet_count'])
        cleaned_tweets_data['followers_count'].append(tweet['user']['followers_count'])
        cleaned_tweets_data['urls'].append(tweet['entities']['urls'])
        cleaned_tweets_data['text'].append(tweet['text'])
        cleaned_tweets_data['lang'].append(tweet['lang'])
        cleaned_tweets_data['country'].append(tweet['place']['country'] if tweet['place'] != None else None)
        cleaned_tweets_data['retweeted_status_id_str'].append(tweet['retweeted_status']['id_str']
                                                              if tweet.get('retweeted_status', None) != None else None)
        cleaned_tweets_data['retweeted_status_user_id_str'].append(tweet['retweeted_status']['user']['id']
                                                                   if tweet.get('retweeted_status',
                                                                                None) != None else None)
        cleaned_tweets_data['in_reply_to_user_id_str'].append(tweet['in_reply_to_user_id_str'])
        cleaned_tweets_data['in_reply_to_status_id_str'].append(tweet['in_reply_to_status_id_str'])
    return cleaned_tweets_data

if __name__ == "__main__":

    try:
        # We open the file
        tweets_data_path = sys.argv[1]
        cleaned_tweets_data = read_tweets_data(tweets_data_path)

        # Transform the Jsoon data in a DataFrame
        tweets = pd.DataFrame()
        tweets['id'] = cleaned_tweets_data['id']
        tweets['name'] = cleaned_tweets_data['name']
        tweets['location'] = cleaned_tweets_data['location']
        tweets['date'] = cleaned_tweets_data['date']
        tweets['time_zone'] = cleaned_tweets_data['time_zone']
        tweets['retweet_count'] = cleaned_tweets_data['retweet_count']
        tweets['followers_count'] = cleaned_tweets_data['followers_count']
        tweets['urls'] = cleaned_tweets_data['urls']
        tweets['text'] = cleaned_tweets_data['text']
        tweets['lang'] = cleaned_tweets_data['lang']
        tweets['country'] = cleaned_tweets_data['country']
        tweets['retweeted_status_id_str'] = cleaned_tweets_data['retweeted_status_id_str']
        tweets['retweeted_status_user_id_str'] = cleaned_tweets_data['retweeted_status_user_id_str']
        tweets['in_reply_to_user_id_str'] = cleaned_tweets_data['in_reply_to_user_id_str']
        tweets['in_reply_to_status_id_str'] = cleaned_tweets_data['in_reply_to_status_id_str']

        # Now count % of retweets and num of unique retweets.
        num_tweets = len(cleaned_tweets_data['id'])
        retweets_count = sum([1 if retweet_id is not None
                              else 0 for retweet_id in cleaned_tweets_data['retweeted_status_id_str']])
        retweets_percent = float(retweets_count) / num_tweets
        unique_retweet_count = Counter([retweet_id for retweet_id in cleaned_tweets_data['retweeted_status_id_str'] if retweet_id is not None])
        num_unique_retweet = len(unique_retweet_count)
        unique_retweet_above_5 = []  # The ids of retweets that has been retweeted above 5 times in our dataset.
        for retweet_id, retweet_count in unique_retweet_count.iteritems():
            if retweet_count >=5 :
                unique_retweet_above_5.append(retweet_id)

        print("%.2f%% of all %d tweets are retweets. There are a total of %d unique retweeted tweets, "
              "out of which %d are retweeted more than 5 times in our collected dataset."
              %(retweets_percent * 100, num_tweets, num_unique_retweet, len(unique_retweet_above_5)))


        if len(sys.argv) >= 3:
            print("Writing file as csv.")
            save_dir = sys.argv[2]
            if os.path.exists(os.path.dirname(save_dir)):
                print("Making the directory to save the csv file.")
                os.mkdir(os.path.dirname(save_dir))
            tweets.to_csv(save_dir, encoding='utf-8')
        else:
            # Print the tweets
            for index, row in tweets.iterrows():
                print(row)

    except IndexError:
        print 'No txt file added'
        sys.exit(2)
    except IOError as e:
        print "I/O error({0}): {1}".format(e.errno, e.strerror)
    # except:
    #     print "Unexpected error:", sys.exc_info()[0]
    #     sys.exit(2)
    #     sys.exit(2)