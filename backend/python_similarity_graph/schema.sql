CREATE TABLE IF NOT EXISTS articles (
    url TEXT PRIMARY KEY,
    site TEXT,
    title TEXT,
    text TEXT,
    images TEXT,
    labels TEXT,
    score REAL,
    cluster_id TEXT,
    cluster_keywords TEXT
);

CREATE TABLE IF NOT EXISTS clusters (
    cluster_id TEXT PRIMARY KEY,
    articles TEXT,
    embedding BLOB
);