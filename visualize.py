

from visualize_util import *

if __name__ == "__main__":
    tweets_file_name = "../measles_streaming_0515.txt"
    trace_file_name = "../measles_trace_0515.tsv"
    # trace_file_name = "../measles_trace_sanity_check.tsv"
    graph = build_graph(trace_file_name)
    # draw_graph(graph, tweets_file_name=tweets_file_name, time_threshold=datetime.date(year, month, day))
    draw_graph(graph, tweets_file_name=tweets_file_name, num_time_threshold=10)
