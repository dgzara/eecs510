import csv
import datetime
import os
import time
import networkx as nx
import matplotlib.pyplot as plt
from math import ceil, log
from dateutil import parser

from analysis import read_tweets_data

def update_contacted_dict(contacted_dict, key, value):
    if key not in contacted_dict:
        contacted_dict[key] = [value]
    else:
        contacted_dict[key].append(value)

def read_trace_file(file_name):
    tweet_id_dict = dict()
    # key = user id. value = (contacted_dict, contacted_by_dict)
    # Both contacted_dict and contacted_by_dict has format: key = user id, value = list of tweet id.
    twitter_accounts_dict = dict()
    with open(file_name, 'r') as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            # No duplicate tweet -- tweet with the same id is not counted twice.
            if "Tweet id" in row and row["Tweet id"] not in tweet_id_dict:
                tweet_id_dict[row["Tweet id"]] = (row["Tweet author"], row["Source id"],
                                                  row["Source author"], row["retweet or reply"])
                if row["Source author"] not in twitter_accounts_dict:
                    twitter_accounts_dict[row["Source author"]] = (dict(), dict())
                # Update contacted by dict
                update_contacted_dict(twitter_accounts_dict[row["Source author"]][1],
                                      row["Tweet author"], row["Tweet id"])
                if row["Tweet author"] not in twitter_accounts_dict:
                    twitter_accounts_dict[row["Tweet author"]] = (dict(), dict())
                # Update contacted by dict
                update_contacted_dict(twitter_accounts_dict[row["Tweet author"]][0],
                                      row["Source author"], row["Tweet id"])

    return tweet_id_dict, twitter_accounts_dict

def twitter_date_to_datetime(twitter_date):
    # ts = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(twitter_date, '%a %b %d %H:%M:%S +0000 %Y'))
    # if isinstance(twitter_date, unicode):
    #     twitter_date = twitter_date.encode('ascii','ignore')
    # ts = datetime.datetime.strptime(twitter_date,'%a %b %d %H:%M:%S +0000 %Y')
    ts = parser.parse(twitter_date)
    return ts

def get_time_thresholds(tweets_data, num_time_threshold):
    # Divide up tweets equally in time. So if we have 10 tweets and num_time_threshold = 5, we return 5 datetime objects
    # each is the time of tweet at index 1, 3, 5, 7, 9 sorted in time.
    times = []
    for i in range(len(tweets_data["date"])):
        tweet_time = twitter_date_to_datetime(tweets_data["date"][i])
        times.append(tweet_time)
    times.sort()

    ret = []
    for i in range(num_time_threshold + 1):
        times_i = min(int(ceil(float(len(times)) * i / num_time_threshold)), len(times) - 1)
        ret.append(times[times_i])
    assert len(ret) == num_time_threshold + 1 and ret[-1] == times[-1]
    return ret

def filter_edges_after_time(edges, edge_tweets, tweets_data, time_threshold):
    ret_edges = []
    ret_edge_weights = []
    ret_edge_tweets = []
    tweets_id_index_dict = {tweets_id:i for i, tweets_id in enumerate(tweets_data['id'])}
    for edge in edges:
        ret_edge_tweets.append([])
        for tweet in edge_tweets[edge]:
            if tweet not in tweets_id_index_dict:
                # If not found, it must be posted before we even started collecting data. Include those by default.
                # raise AttributeError("Cannot find tweet id %s in tweets_data." %(tweet))
                # ret_edge_tweets[-1].append(edge)
                pass
            else:
                i = tweets_id_index_dict[tweet]
                tweet_time = twitter_date_to_datetime(tweets_data["date"][i])
                if tweet_time <= time_threshold:
                    ret_edge_tweets[-1].append(edge)
        if len(ret_edge_tweets[-1]) > 0:
            ret_edges.append(edge)
            ret_edge_weights.append(len(ret_edge_tweets[-1]))
        else:
            ret_edge_tweets.pop()
    return ret_edges, ret_edge_weights, ret_edge_tweets

def filter_edges_and_weights(edges, weights, allowed_nodes):
    if not isinstance(allowed_nodes, set):
        allowed_nodes = set(allowed_nodes)
    allowed_edges = []
    allowed_weights = []
    for i in range(len(edges)):
        if edges[i][0] in allowed_nodes and edges[i][1]:
            allowed_edges.append(edges[i])
            allowed_weights.append(weights[i])
    return allowed_edges, allowed_weights

def build_graph(trace_file_name):
    """
    Each node is a twitter account. Each edge is an interaction between two accounts. The weight of the edge is the
    number of interactions.
    :return:
    """

    tweet_id_dict, twitter_accounts_dict = read_trace_file(trace_file_name)

    g = nx.Graph()


    for user_id, (contacted_dict, contacted_by_dict) in twitter_accounts_dict.iteritems():
        for contacted_by_user_id, contacted_by_tweet_ids in contacted_by_dict.iteritems():
            g.add_edge(user_id, contacted_by_user_id, weight=len(contacted_by_tweet_ids), tweets = contacted_by_tweet_ids)

    return g

def draw_graph(graph, with_labels=True, weight_threshold=50, num_time_threshold=None, tweets_file_name=None):
    # First draw the nodes with degree more than threshold. They are either contacted by a lot or contact others a lot.
    try:
        pos = nx.nx_agraph.graphviz_layout(graph)
    except:
        print('using spring layout.')
        pos = nx.spring_layout(graph)

    if num_time_threshold is None:
        time_thresholds = [None]
    else:
        if not os.path.exists(tweets_file_name):
            raise IOError("Cannot find file %d. The tweets data file generated by stream_and_trace.py is required."
                          % (tweets_file_name))
        tweets_data = read_tweets_data(tweets_file_name)
        time_thresholds = get_time_thresholds(tweets_data, num_time_threshold)

    fig, ax = plt.subplots()
    _, weights = zip(*nx.get_edge_attributes(graph, 'weight').items())
    colorbar_range = range(min(weights),max(weights)+1)

    for time_threshold in time_thresholds:
        # assert isinstance(time_threshold, datetime.time) or time_threshold is None
        nodes = graph.nodes(data=False)
        edges, weights = zip(*nx.get_edge_attributes(graph, 'weight').items())

        if time_threshold is not None:
            edge_tweets = nx.get_edge_attributes(graph, 'tweets')
            edges, weights, edge_tweets = filter_edges_after_time(edges, edge_tweets, tweets_data, time_threshold)

        node_degrees = []
        node_sizes = []
        leaders = []
        leaders_node_degrees=[]
        leaders_node_degrees_log=[]
        leaders_labels={}
        followers = []
        followers_node_degrees=[]
        followers_node_degrees_log=[]
        for node in nodes:
            weight = graph.degree(node, weight='weight')
            node_degrees.append(weight)
            node_sizes.append(max(log(weight),1))
            if weight >= weight_threshold:
                leaders.append(node)
                leaders_node_degrees.append(weight)
                leaders_node_degrees_log.append(max(log(weight),1))
                leaders_labels[node]=node
            else:
                followers.append(node)
                followers_node_degrees.append(weight)
                followers_node_degrees_log.append(max(log(weight),1))

        # Draw step
        # nodes
        nx.draw_networkx_nodes(graph, pos, width=5.0, alpha=1.0, node_size=leaders_node_degrees, nodelist=leaders,
                               node_color=leaders_node_degrees_log, node_cmap=plt.cm.Greens)
        nx.draw_networkx_nodes(graph, pos, width=5.0, alpha=1.0, node_size=followers_node_degrees, nodelist=followers,
                               node_color=followers_node_degrees_log, node_cmap=plt.cm.Blues)
        if time_threshold is not None:
            # There are some nodes that we would not like to include.
            edges, weights = filter_edges_and_weights(edges, weights, nodes)
        edge_colors = [weight for weight in weights]
        edge_widths = [min(weight, 3) for weight in weights]
        edges_drawn = nx.draw_networkx_edges(graph, pos,alpha=0.05, width=edge_widths, edgelist=edges, edge_color=edge_colors, edge_cmap=plt.cm.inferno)
        if edges_drawn is not None:
            cb = fig.colorbar(edges_drawn, ticks=colorbar_range)
        else:
            cb = None
        plt.axis('off')

        file_name = "till_%s_%s_%s_%s_%s_%s.eps" %(time_threshold.year, time_threshold.month, time_threshold.day,
                                                   time_threshold.hour, time_threshold.minute, time_threshold.second, ) \
            if time_threshold is not None else "all.eps"
        plt.savefig(file_name, format='eps', dpi=1000)

        # Add labels only on the zoomed version.
        if with_labels:
            nx.draw_networkx_labels(graph, pos, leaders_labels, font_size=10, font_color='r')

        zoomed_file_name = os.path.basename(file_name) + "_zoomed.eps"
        xlim_min, xlim_max = ax.get_xlim()
        ylim_min, ylim_max = ax.get_ylim()
        new_xlim_min = (xlim_max - xlim_min) * 4 / 10 + xlim_min
        new_xlim_max = (xlim_max - xlim_min) * 6 / 10 + xlim_min
        new_ylim_min = (ylim_max - ylim_min) * 4 / 10 + ylim_min
        new_ylim_max = (ylim_max - ylim_min) * 6 / 10 + ylim_min
        ax.set_xlim(new_xlim_min, new_xlim_max)
        ax.set_ylim(new_ylim_min, new_ylim_max)
        plt.savefig(zoomed_file_name, format='eps', dpi=1000)
        plt.cla()
        if cb is not None:
            cb.remove()
