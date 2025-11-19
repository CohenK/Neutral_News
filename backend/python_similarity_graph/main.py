import os
import pathlib
from sentence_transformers import SentenceTransformer
from graph import Graph
from utils import extract_dir_data, append_to_json_array


def main():
    curr_dir = pathlib.Path.cwd().parent
    rss_dir = os.path.join(curr_dir, "rust_article_fetcher", "rss")
    crawled_data_dir = os.path.join(curr_dir, "rust_article_fetcher", "crawled_data")

    article_data = []
    article_data += extract_dir_data(rss_dir)
    article_data += extract_dir_data(crawled_data_dir)
    for a in article_data:
        append_to_json_array(os.path.join("data", "articles.json"), a)


    model = SentenceTransformer("all-MiniLM-L6-v2")
    contents = [a["content"] for a in article_data]
    embeddings = model.encode(contents, normalize_embeddings=True)

    idToArticle = {}
    for a in article_data:
        idToArticle[a["url"]] = a

    graph = Graph(embeddings, article_data, 0.8)
    graph.compute_edges()
    graph.cluster()
    graph.write_cluster(os.path.join("data","clusters.json"))
    graph.store_graph()

main()