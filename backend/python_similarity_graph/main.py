import os
import re

def extract_dir_data(dir_path):
    """ given a directory get the data in all its files """
    result = []
    for file in os.listdir(dir_path):
        filepath = dir_path + "\\" + file
        f = open(filepath, "r")
        result.append(f.read())
        f.close()
    return result

def main():
    curr_dir = os.getcwd()
    rss_dir = os.path.join(curr_dir, "rust_article_fetcher", "rss")
    crawled_data_dir = os.path.join(curr_dir, "rust_article_fetcher", "crawled_data")

    article_data = []
    article_data += extract_dir_data(rss_dir)
    article_data += extract_dir_data(crawled_data_dir)
    
    # clean article data by replacing newlines with spaces
    for article in article_data:
        article = re.sub("\n", " ", article)

main()