#!/usr/bin/python

import json

def parse_json(data):
    return json.loads(data)

def get_tweet_nested_parameter(tweet, parameters):
    """

    :param tweet: the tweet in json format.
    :param parameters: a list of string parameters of the tweet, or just one string parameter.
    :return: if the list is like [x,y,z] then return tweet[x][y][z].
    If any of the parameter does not exist, return None.
    """
    assert isinstance(parameters, list) or isinstance(parameters, str)
    if isinstance(parameters, str):
        return tweet.get(parameters, None)
    elif len(parameters) == 1:
        return tweet.get(parameters[0], None)
    elif len(parameters) == 0:
        return tweet
    else:
        subparameter = tweet.get(parameters[0], None)
        if subparameter is None:
            return None
        else:
            return get_tweet_nested_parameter(subparameter, parameters[1:])


def get_retweet_status_id_str(tweet):
    if 'id_str' not in tweet:
        return None
    return get_tweet_nested_parameter(tweet, ['retweeted_status', 'id_str'])

def get_retweet_status_user_id(tweet):
    if 'id_str' not in tweet:
        return None
    return get_tweet_nested_parameter(tweet, ['retweeted_status', 'user', 'id'])



def get_in_reply_to_status_id_str(tweet):
    if 'id_str' not in tweet:
        return None
    return get_tweet_nested_parameter(tweet, ['in_reply_to_user_id_str'])


def get_in_reply_to_user_id_str(tweet):
    if 'id_str' not in tweet:
        return None
    return get_tweet_nested_parameter(tweet, ['in_reply_to_status_id_str'])
