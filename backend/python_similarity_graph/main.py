import os
import pathlib
from graph import Graph
from utils import extract_dir_data, append_to_json_array
from nlp import infer
import time

def main():
    curr_dir = pathlib.Path.cwd().parent
    rss_dir = os.path.join(curr_dir, "rust_article_fetcher", "rss")
    crawled_data_dir = os.path.join(curr_dir, "rust_article_fetcher", "crawled_data")

    # coalesce all news articles both from RSS and crawling into a list
    start_time = time.perf_counter()
    article_data = []
    article_data += extract_dir_data(rss_dir)
    article_data += extract_dir_data(crawled_data_dir)
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Articles coalesce + cleanup time: {elapsed_time:.4f} seconds")

    # rate all articles as left, neutral or right
    start_time = time.perf_counter()
    ratings = infer(article_data)
    for article, rating in zip(article_data, ratings):
        article["labels"] = rating[0]
        article["score"] = rating[1]
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Articles rating time: {elapsed_time:.4f} seconds")

    # run graph to map out clusters of related articles
    start_time = time.perf_counter()
    graph = Graph(article_data, 0.8)
    graph.compute_edges()
    graph.cluster()
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Article Graphing time: {elapsed_time:.4f} seconds")

if __name__ == "__main__":
    main()