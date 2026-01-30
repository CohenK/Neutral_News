import { useSearchParams, useOutletContext } from "react-router-dom";
import { Link } from "react-router-dom";
import Loading from "./Loading";
import type { Article, AppCtx, Pair } from "./types";
import { useEffect, useState } from "react";
import Rating from "./Rating";
import ArticleCard from "./ArticleCard";

function ArticleView() {
  const defaultArticle: Article = {
    id: 0,
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
  const { articles, pairs, clusters, loading } = useOutletContext<AppCtx>();
  const [article, setArticle] = useState<Article>(defaultArticle);
  const [mainlist, setMainlist] = useState<string[]>([]);
  const [offlist, setOfflist] = useState<string[]>([]);
  const [secondaryUrl, setSecondaryUrl] = useState<string>("");
  const [relatedArticles, setRelatedArticles] = useState<Article[]>([]);
  const [meta, setMeta] = useState(false);

  useEffect(() => {
    const target = articles.find((article) => article.id === Number(query!))!;
    setArticle(target);
    const all_matches = pairs.filter(
      (pair: Pair) => pair.source_url === article.url,
    );
    const relatedArticleInfo = clusters[target.cluster_id]
      .map((url) => articles.find((article) => article.url === url))
      .filter((a): a is Article => a !== undefined);
    setRelatedArticles(relatedArticleInfo);

    return () => {};
  }, [query, secondaryUrl]);

  const handleMeta = () => {
    setMeta((m) => !m);
  };

  const handleSecondary = (url: string) => {
    setSecondaryUrl(url);
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
              <ArticleCard article={article} match_list={mainlist} />
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

export default ArticleView;
