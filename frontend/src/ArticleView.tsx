import { useSearchParams, useOutletContext } from "react-router-dom";
import Loading from "./Loading";
import type { Article, AppCtx, Pair } from "./types";
import { useEffect, useState } from "react";
import ArticleCard from "./ArticleCard";
import MetaCard from "./MetaCard";

function ArticleView() {
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
  const { articles, pairs, clusters, urlMap, loading } =
    useOutletContext<AppCtx>();
  const [article, setArticle] = useState<Article>(defaultArticle);
  const [mainlist, setMainlist] = useState<string[]>([]);
  const [offlist, setOfflist] = useState<string[]>([]);
  const [secondaryUrl, setSecondaryUrl] = useState<string>("");
  const [relatedArticles, setRelatedArticles] = useState<Article[]>([]);
  const [meta, setMeta] = useState(false);
  const [matches, setMatches] = useState<Pair[]>([]);

  useEffect(() => {
    const target = articles[query!];
    setArticle(target);
    const all_matches = pairs.filter(
      (pair: Pair) => pair.source_url === target.url,
    );
    setMatches(all_matches);
    const relatedArticleInfo = clusters[target.cluster_id]
      .map((url) => articles[String(urlMap[url])])
      .filter((a): a is Article => a !== undefined && a.url !== target.url);
    setRelatedArticles(relatedArticleInfo);

    return () => {};
  }, [query]);

  useEffect(() => {
    const filtered = matches.filter(
      (match) => match.match_url === secondaryUrl,
    );
    const main = filtered.map((match) => match.source_sentence);
    const off = filtered.map((match) => match.match_sentence);
    setMainlist(main);
    setOfflist(off);

    //break up both paragraphs into plain text and their highlighted sentences for pair-wise indicators
  }, [secondaryUrl]);

  const handleMeta = () => {
    setMeta((m) => !m);
  };

  const handleCompare = (url: string) => {
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
                className="absolute top-[1rem] right-[1rem] w-[3rem] h-[3rem] bg-rule-light rounded-full border-2 border-solid border-rule-heavy text-ink-main text-[1.5rem] cursor-pointer hover:bg-rule-heavy"
              >
                i
              </button>
              <ArticleCard article={article} match_list={mainlist} />
            </div>
            <div
              className={`${meta ? "translate-x-0" : "translate-x-full"} flex flex-col bg-paper-alt w-[50%] h-[calc(100vh-4rem)] overflow-hidden transition-all duration-500 ease-in-out px-10`}
            >
              <MetaCard
                article={article}
                offlist={offlist}
                meta={meta}
                relatedArticles={relatedArticles}
                urlMap={urlMap}
                handleCompare={handleCompare}
              />
            </div>
          </div>
        </>
      )}
    </>
  );
}

export default ArticleView;
