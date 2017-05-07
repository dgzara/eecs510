#!/usr/bin/python

"""
This file do the usual stream listening, but for each tweet it receives, it checks whether it is a retweet.
If so, it also downloads the source tweet.
Example usage: Correct format: python stream_and_trace.py query save_path
"""

import sys, json, os
import tweepy
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from credentials import *
from util import *


class StdOutListener(StreamListener):
    """ A listener handles tweets that are received from the stream.
    This is a basic listener that just prints received tweets to stdout.

    """

    def __init__(self, api, tweet_retweet_pair_file_name):
        super(StdOutListener, self).__init__(api)
        self.tweet_retweet_pair_file_name = tweet_retweet_pair_file_name
        if os.path.exists(self.tweet_retweet_pair_file_name):
            raise IOError("The file %s already exists! "
                          "I raises an error in order to prevent overwriting old file."
                          %(self.tweet_retweet_pair_file_name))
        with open(self.tweet_retweet_pair_file_name, 'w') as f:
            f.write("Tweet id\tTweet author\tSource id\tSource author\retweet or reply\n")

    def on_data(self, data):
        data = data.rstrip()
        print data
        trace(data, self.api, self.tweet_retweet_pair_file_name)
        return True

    def on_error(self, status):
        print(status)


def trace(tweet, api, record_file_name):
    """
    Given the id of one tweet, check if it is a retweet or reply. If so, print the source and recursively call the same function
    on the source id
    :param tweet: the tweet, either as a unicode string, a string,
    or tweepy.Status which is the return of api.get_status(tweet_id)
    :param api: the twitter api
    :param record_file_name: the file name to which a list of (tweet_id, source_id) will be saved.
    :return: None
    """
    # assert isinstance(id_str,str) and api is not None
    # tweet = api.get_status(id_str)
    if isinstance(tweet, unicode) or isinstance(tweet, str):
        data = json.loads(tweet)
    elif isinstance(tweet, tweepy.Status):
        data = tweet._json
    else:
        raise AttributeError("Illegal input tweet in trace function. "
                             "It has to be a unicode, a string, or tweepy.Status")
    tweet_id = get_tweet_nested_parameter(data, 'id_str')
    tweet_user_id = get_tweet_nested_parameter(data, ['user','id_str'])
    retweet_id = get_retweet_status_id_str(data)  # This is the id of the tweet being retweeted, a.k.a. source tweet.
    if retweet_id is not None:
        retweet_user_id = get_retweet_status_user_id(data)
        retweet = api.get_status(retweet_id)
        if not int(tweet_id) >= int(retweet_id):
            raise AssertionError("Something went wrong! "
                                 "Retweet id should always be older a.k.a. larger than the source id.")
        if retweet and retweet_id != tweet_id:
            print(json.dumps(retweet._json))
            with open(record_file_name, 'a') as f:
                f.write("%s\t%s\t%s\t%s\t%s\n" % (tweet_id, tweet_user_id, retweet_id, retweet_user_id, "retweet"))
            trace(retweet, api, record_file_name)

    reply_id = get_in_reply_to_status_id_str(data)
    if reply_id is not None:
        reply_user_id = get_in_reply_to_user_id_str(data)
        source = api.get_status(reply_user_id)
        if not int(tweet_id) >= int(reply_id):
            raise AssertionError("Something went wrong! "
                                 "reply id should always be older a.k.a. larger than the source id.")
        if source and reply_id != tweet_id:
            print(json.dumps(source._json))
            with open(record_file_name, 'a') as f:
                f.write("%s\t%s\t%s\t%s\t%s\n" % (tweet_id, tweet_user_id, reply_id, reply_user_id, "reply"))
            trace(source, api, record_file_name)


if __name__ == '__main__':

    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)

    # We get the query
    try:
        query = sys.argv[1]
        save_path = sys.argv[2]
    except IndexError:
        print 'Correct format: python stream_and_trace.py query save_path'
        sys.exit(2)

    # We add the query in the stream filter
    stream = Stream(auth, StdOutListener(tweepy.API(auth),save_path))
    stream.filter(track=[query])



