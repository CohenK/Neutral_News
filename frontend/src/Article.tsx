import { useSearchParams, useOutletContext } from "react-router-dom";
import { Link } from "react-router-dom";
import Loading from "./Loading";
import type { Article, AppCtx } from "./types";
import { useEffect, useState } from "react";
import Rating from "./Rating";

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
  const [meta, setMeta] = useState(false);

  useEffect(() => {
    const target = articles[Number(query!)];
    setArticle(target);

    return () => {};
  }, [query]);

  const handleMeta = () => {
    setMeta((m) => !m);
  };

  return (
    <>
      {loading ? (
        <Loading />
      ) : (
        <>
          <div className="flex">
            <div
              className={`${meta ? "max-w-[50%] translate-x-0" : "max-w-[75%] translate-x-[16.67%]"} relative flex flex-col bg-paper-main min-w-0 h-[calc(100vh-4rem)] overflow-hidden px-20 transition-all duration-500 ease-in-out`}
            >
              <button
                onClick={handleMeta}
                className="absolute top-[1rem] right-[1rem] w-[3rem] h-[3rem] bg-rule-light rounded-full border-2 border-solid border-rule-heavy text-ink-main text-[1.5rem] hover:bg-rule-heavy"
              >
                i
              </button>
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
              <div className="text-ink-soft text-[1.5rem] text-justify overflow-y-auto no-scrollbar min-w-0">
                {article.article}
              </div>
            </div>
            <div
              className={`${meta ? "translate-x-0" : "translate-x-full"} flex flex-col items-center bg-paper-alt w-[50%] h-[calc(100vh-4rem)] transition-all duration-500 ease-in-out`}
            >
              <Rating
                score={article.score}
                rating={article.labels}
                toggle={meta}
              />
            </div>
          </div>
        </>
      )}
    </>
  );
}

export default Article;
