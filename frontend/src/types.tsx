export type Article = {
  url: string;
  site: string;
  title: string;
  article: string;
  images: string[];
  labels: string;
  score: Number;
  cluster_id: string;
  article_keywords: string[];
};

export type AppCtx = {
  articles: Article[];
  loading: boolean;
};
