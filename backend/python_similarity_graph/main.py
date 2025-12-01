import os
import pathlib
from graph import Graph
from utils import extract_dir_data
from nlp import infer

def main():
    curr_dir = pathlib.Path.cwd().parent
    rss_dir = os.path.join(curr_dir, "rust_article_fetcher", "rss")
    crawled_data_dir = os.path.join(curr_dir, "rust_article_fetcher", "crawled_data")

    # coalesce all news articles both from RSS and crawling into a list
    article_data = []
    article_data += extract_dir_data(rss_dir)
    article_data += extract_dir_data(crawled_data_dir)

    # rate all articles as left, neutral or right
    for a in article_data:
        labels, score = infer(a["content"])
        a["labels"] = labels
        a["score"] = score

    # run graph to map out clusters of related articles
    graph = Graph(article_data, 0.8)
    graph.compute_edges()
    graph.cluster()

if __name__ == "__main__":
    main()