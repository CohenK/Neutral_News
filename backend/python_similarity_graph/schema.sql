CREATE TABLE IF NOT EXISTS article (
  url           TEXT PRIMARY KEY,      
  site          TEXT NOT NULL,         
  title         TEXT,                  
  text          TEXT NOT NULL,         
  cluster_id    TEXT,                  
  cluster_keywords TEXT                   
);

CREATE INDEX IF NOT EXISTS idx_article_cluster ON article(cluster_id);
CREATE INDEX IF NOT EXISTS idx_article_site    ON article(site);
CREATE INDEX IF NOT EXISTS idx_article_title   ON article(title);