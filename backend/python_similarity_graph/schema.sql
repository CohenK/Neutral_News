CREATE TABLE IF NOT EXISTS paragraph (
  id TEXT PRIMARY KEY,
  doc_id TEXT,
  para_index INTEGER,
  site TEXT,
  lang TEXT,
  ts TEXT,
  text TEXT,
  cluster_id TEXT,
  cluster_label TEXT
);

CREATE INDEX IF NOT EXISTS idx_ts ON paragraph(ts);
CREATE INDEX IF NOT EXISTS idx_cluster ON paragraph(cluster_id);
