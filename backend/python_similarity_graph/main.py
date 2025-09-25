import os
import re
import pathlib
import json
from sentence_transformers import SentenceTransformer
from graph import Graph


def extract_dir_data(dir_path):
    """ given a directory get article data in all its files and clean the data """
    result = []
    for file in os.listdir(dir_path):
        filepath = os.path.join(dir_path,file)
        with open(filepath, 'r', encoding='utf-8', errors='strict') as f:
            data = json.load(f)
        # clean article data by replacing newlines with spaces
        data["content"] = data["content"].replace('\n', ' ')
        data["content"] = data["content"].replace('\"', '"')
        data["content"] = data["content"].replace('\t', ' ')
        data["content"] = re.sub(r"\s+", " ", data["content"]).strip()
        result.append(data)
        f.close()
    return result

def append_to_json_array(path, obj):
    """ write all article json data for debugging purposes """
    p = pathlib.Path(path)
    if p.exists() and p.stat().st_size > 0:
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = []
        if isinstance(data, list):
            data.append(obj)
        else:
            data = [data, obj]  # if file held a single object
    else:
        data = [obj]
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def write_cluster(path, dict):
    """ write cluster dictionary to a field in json format for debugging """
    p = pathlib.Path(path)
    with open(p,'w') as f:
        json.dump(dict,f, indent=4)
    f.close()


def main():
    curr_dir = pathlib.Path.cwd().parent
    rss_dir = os.path.join(curr_dir, "rust_article_fetcher", "rss")
    crawled_data_dir = os.path.join(curr_dir, "rust_article_fetcher", "crawled_data")

    article_data = []
    article_data += extract_dir_data(rss_dir)
    article_data += extract_dir_data(crawled_data_dir)
    for a in article_data:
        append_to_json_array("articles.json",a)


    model = SentenceTransformer("all-MiniLM-L6-v2")
    contents = [a["content"] for a in article_data]
    embeddings = model.encode(contents, normalize_embeddings=True)

    idToArticle = {}
    for a in article_data:
        idToArticle[a["url"]] = a

    graph = Graph(embeddings, article_data, 0.8)
    graph.compute_edges()
    graph.cluster()
    write_cluster("clusters.json",graph._clusterIds)

main()