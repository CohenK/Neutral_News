CREATE TABLE IF NOT EXISTS articles (
    url TEXT PRIMARY KEY,
    site TEXT,
    title TEXT,
    text TEXT,
    images TEXT,
    labels TEXT,
    score REAL,
    cluster_id TEXT,
    article_keywords TEXT
);

CREATE TABLE IF NOT EXISTS clusters (
    cluster_id TEXT PRIMARY KEY,
    articles TEXT,
    sentences TEXT,
    meta TEXT
);

CREATE TABLE IF NOT EXISTS pairs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cluster_id TEXT,
    source_sentence TEXT,
    source_url TEXT,
    match_sentence TEXT,
    match_url TEXT,
    score REAL
);
