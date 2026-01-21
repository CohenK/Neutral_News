import { useSearchParams, useOutletContext } from "react-router-dom";
import { Link } from "react-router-dom";
import type { Article, AppCtx } from "./types";
import { useEffect, useState } from "react";

function Article() {
  const defaultArticle: Article = {
    url: "",
    site: "",
    title: "",
    article: "",
    images: [],
    labels: "",
    score: 0,
    cluster_id: "",
    article_keywords: [],
  };

  const [searchParams] = useSearchParams();
  const query = searchParams.get("q");
  const { articles, loading } = useOutletContext<AppCtx>();
  const [article, setArticle] = useState<Article>(defaultArticle);

  useEffect(() => {
    const target = articles[Number(query!)];
    setArticle(target);

    return () => {};
  }, [query]);

  if (loading) return <div>Loading…</div>;

  return (
    <div className="flex flex-col bg-paper-main h-[calc(100vh-4rem)] overflow-hidden max-w-[75%] mx-auto px-10">
      <div className="flex justify-center text-[3rem] text-ink-main">
        {article.title}
      </div>
      <div className="text-accent-blue text-[1.5rem]">
        News Outlet: {article.site}
      </div>
      <div className="flex gap-2 text-[1.5rem]">
        <div className="text-accent-blue">Original article:</div>
        <a
          className="text-accent-red underline"
          href={article.url}
          target="_blank"
          rel="noopener noreferrer"
        >
          Link
        </a>
      </div>
      <div className="text-accent-blue text-[1.5rem]">Article:</div>
      <div className="text-ink-soft text-[1.5rem] overflow-y-auto no-scrollbar">
        {article.article}
      </div>
    </div>
  );
}

export default Article;
