import os
import pathlib
import json
from sentence_transformers import SentenceTransformer
from graph import Graph
from clean import clean_article

def extract_dir_data(dir_path):
    """ given a directory get article data in all its files and clean the data """
    result = []
    for file in os.listdir(dir_path):
        filepath = os.path.join(dir_path,file)
        with open(filepath, 'r', encoding='utf-8', errors='strict') as f:
            data = json.load(f)
        # clean article data by replacing newlines with spaces
        data["content"] = clean_article(data["content"])
        result.append(data)
        f.close()
    return result

# def clean_article(data):
#     """ remove new outlet boiler plate from article text """
#     res = data

#     bad = [
#         '\t', '\"',
#         'Al Jazeera', 'Al Jazeera English', 'Published On', 'By Al Jazeera Staff', 'Source: Al Jazeera',
#         'All rights reserved', 'Sign up for our newsletter', '(AP)', 'Associated Press',
#         'The Associated Press contributed to this report.',
#         'All rights reserved. This material may not be published, broadcast, rewritten or redistributed.',
#         'BBC News', 'BBC', 'See full coverage on BBC News.', '© BBC.', 'The BBC is not responsible for the content of external sites.',
#         'Deutsche Welle', 'DW', '(Reuters, AFP, dpa)', 'This article was originally written in German.',
#         'NPR', 'This text may not be in its final form and may be updated or revised.',
#         'PBS NewsHour', 'Watch tonight’s PBS NewsHour for more coverage.',
#         'Join our mailing list', 'Subscribe for more stories', 'Click here to read more', 'Share this article'
#     ]
    
#     for b in bad:
#         res = res.replace(b, '')
    
#     patterns = [
#         # BBC
#         r'(?im)^By\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+,\s*BBC\s+News\.?\s*$',
#         # general
#         r'(?i)\bfirst\s+published\s+on\s+(?:\d{1,2}\s+\w+\s+\d{4}|\w+\s+\d{1,2},?\s+\d{4})', '', res,
#         r'(?i)\bedited\s+by\s+[A-Z][\w\s.-]+', '', res,
#         r'(?i)\breporting\s+by\s+[A-Z][\w\s.-]+', '', res,
#         r'(?i)\bfollow\s+[A-Z][\w\s.-]+\s+on\s+[A-Z][\w\s.-]+', '', res,
#         r'(?i)\bsign\s+up\s+for\s+the\s+[A-Z][\w\s.-]+\s+(?:newsletter|newspaper)', '', res,
#         r'(?i)\bthis\s+story\s+originally\s+appeared\s+on\s+[A-Z][\w\s.-]+', '', res,
#         r'(?im)(copyright\s*)?©\s*\d{4}\s*[\w\s.-]+\.?\s*all\s+rights\s+reserved\.?', '', res,
#         r'(?i)\blisten\s+to\s+this\s+story\s+on\s+(?:all\s+things\s+considered|morning\s+edition)[.!]?\s*', '', res,
#     ]

#     for p in patterns:
#         res = re.sub(p,'',res)

#     res = re.sub(r'(?im)^[^\n]*\((?:AP\s+Photo|AP)\s*/[^)]+\)[^\n]*$', '', res)
#     res = re.sub(r'\s*\(AP\s+Photo/[^)]+\)', '', res)
#     res = re.sub(r'(?im)(?:\s*(?:copyright\s*)?©?\s*20\d{2}\s*(?:the\s+)?associated\s+press\.?\s*all\s+rights\s+reserved\.?)+\s*', '', res)
#     res = re.sub(r'(?im)^\s*AP\s+[A-Z]{2,}:\s*\S+\s*$', '', res)
#     res = re.sub(r'(?im)^\s*\(AP\)\s*$', '', res)
#     res = re.sub(r'(?im)^\s*CORRECTION\b.*$', '', res)


#     res = res.replace('\r\n', '\n').replace('\r', '\n')
#     res = '\n'.join(line for line in (ln.strip() for ln in res.split('\n')) if line)
#     res = re.sub(r'[ \t\u00A0]+', ' ', res)
    
#     res = res.strip()
    
#     return res

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
    graph.store_graph()

main()