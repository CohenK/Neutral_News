export type Article = {
  id: number;
  url: string;
  site: string;
  title: string;
  article: string;
  images: string[];
  labels: string;
  score: number;
  cluster_id: string;
  article_keywords: string[];
};

export type Pair = {
  id: number;
  cluster_id: string;
  source_sentence: string;
  source_url: string;
  match_sentence: string;
  match_url: string;
  score: number;
};

export type Cluster = Record<string, string[]>;

export type AppCtx = {
  articles: Record<string, Article>;
  pairs: Pair[];
  clusters: Record<string, string[]>;
  urlMap: Record<string, string>;
  loading: boolean;
};
