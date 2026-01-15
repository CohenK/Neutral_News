import shutil
import pathlib
from os.path import join

def export():
    script_dir = pathlib.Path(__file__).resolve().parent
    files = ["articles.json", "clusters.json","pairs.json"]

    neutral_news = script_dir.parent.parent.parent
    src_dir = pathlib.Path(join(neutral_news, "backend", "python_similarity_graph", "data"))
    out_dir = pathlib.Path(join(neutral_news, "frontend", "public", "data"))
    out_dir.mkdir(parents=True, exist_ok=True)

    for file in files:
        shutil.copy2(pathlib.Path(join(src_dir,file)), out_dir)

if __name__ == "__main__":
    export()