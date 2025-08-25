import os
import re
import sqlite3, pathlib
from sentence_transformers import SentenceTransformer
from graph import Graph


def extract_dir_data(dir_path):
    """ given a directory get article data in all its files """
    result = []
    for file in os.listdir(dir_path):
        filepath = dir_path + "\\" + file
        f = open(filepath, "r")
        # clean article data by replacing newlines with spaces
        # result.append(re.sub("\n", " ", f.read()))
        f.close()
    return result


def main():
    curr_dir = os.getcwd()
    rss_dir = os.path.join(curr_dir, "..", "rust_article_fetcher", "rss")
    crawled_data_dir = os.path.join(curr_dir, "..", "rust_article_fetcher", "crawled_data")

    article_data = []
    article_data += extract_dir_data(rss_dir)
    article_data += extract_dir_data(crawled_data_dir)

    model = SentenceTransformer("all-MiniLM-L6-v2")
    contents = [a.content for a in article_data]
    ids = [a.url for a in article_data]
    embeddings = model.encode(contents, normalize_embeddings=True)




main()