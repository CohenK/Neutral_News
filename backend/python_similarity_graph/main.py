import os
import pathlib
from sentence_transformers import SentenceTransformer
from graph import Graph
from utils import extract_dir_data, add_to_json_file
from nlp import infer

def main():
    curr_dir = pathlib.Path.cwd().parent
    rss_dir = os.path.join(curr_dir, "rust_article_fetcher", "rss")
    crawled_data_dir = os.path.join(curr_dir, "rust_article_fetcher", "crawled_data")

    article_data = []
    article_data += extract_dir_data(rss_dir)
    article_data += extract_dir_data(crawled_data_dir)
    for a in article_data:
        labels, score = infer(a["content"])
        a["labels"] = labels
        a["score"] = score
        add_to_json_file(os.path.join("data", "articles.json"), a["url"], a)


    model = SentenceTransformer("all-MiniLM-L6-v2")
    contents = [a["content"] for a in article_data]
    embeddings = model.encode(contents, normalize_embeddings=True)

    # article_sentences = {}
    # for a in article_data:
    #     article_sentences[a["url"]] = split_into_sentences(a["content"])


    idToArticle = {}
    for a in article_data:
        idToArticle[a["url"]] = a

    graph = Graph(embeddings, article_data, 0.8)
    graph.compute_edges()
    graph.cluster()
    graph.write_cluster(os.path.join("data","clusters.json"))
    graph.store_graph()

main()