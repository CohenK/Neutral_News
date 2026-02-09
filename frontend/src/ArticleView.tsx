import { useSearchParams, useOutletContext } from "react-router-dom";
import Loading from "./Loading";
import type { Article, AppCtx, Pair } from "./types";
import { useEffect, useState } from "react";
import ArticleCard from "./ArticleCard";
import MetaCard from "./MetaCard";
import CompareView from "./CompareView";

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
  const { articles, pairs, clusters, urlMap, loading } =
    useOutletContext<AppCtx>();
  const [article, setArticle] = useState<Article>(defaultArticle);
  const [offArticle, setOffArticle] = useState<Article | undefined>(undefined);
  const [mainList, setMainList] = useState<string[]>([]);
  const [offList, setOffList] = useState<string[]>([]);
  const [secondaryUrl, setSecondaryUrl] = useState<string>("");
  const [relatedArticles, setRelatedArticles] = useState<Article[]>([]);
  const [meta, setMeta] = useState(false);
  const [matches, setMatches] = useState<Pair[]>([]);
  const [compare, setCompare] = useState<boolean>(false);

  useEffect(() => {
    closeCompare();
    if (!query) return;
    const target = articles[query];

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
  }, [query, articles, pairs, clusters, urlMap]);

  useEffect(() => {
    const id = urlMap[secondaryUrl];
    setOffArticle(articles[id]);
    const filtered = matches.filter(
      (match) => match.match_url === secondaryUrl,
    );
    console.log("matches: ", filtered.length);
    const main = filtered.map((match) => match.source_sentence);
    const off = filtered.map((match) => match.match_sentence);
    setMainList(main);
    setOffList(off);
  }, [query, secondaryUrl, matches, articles, urlMap]);

  const handleMeta = () => {
    setMeta((m) => !m);
  };

  const openCompare = (url: string) => {
    setCompare(true);
    setSecondaryUrl(url);
  };

  const closeCompare = () => {
    setCompare(false);
    setSecondaryUrl("");
    setOffArticle(undefined);
    setMainList([]);
    setOffList([]);
  };
  const compareReady =
    compare &&
    offArticle !== undefined &&
    mainList.length > 0 &&
    offList.length > 0;

  console.log(
    `compareReady: ${compareReady}, mainlist length: ${mainList.length}, offlist length: ${offList.length}, offArticle: ${offArticle?.title}`,
  );

  return (
    <>
      {loading ? (
        <Loading />
      ) : (
        <div className="fixed">
          <div className={`${compareReady ? "pointer-events-none" : ""} flex`}>
            <div
              className={`${meta ? "max-w-[50%] translate-x-0" : "max-w-[75%] translate-x-[16.67%]"} relative flex flex-col bg-paper-main min-w-0 h-[calc(100vh-4rem)] overflow-hidden px-20 transition-all duration-500 ease-in-out`}
            >
              <button
                onClick={handleMeta}
                className="absolute top-[1rem] right-[1rem] w-[3rem] h-[3rem] bg-rule-light rounded-full border-2 border-solid border-rule-heavy text-ink-main text-[1.5rem] cursor-pointer hover:bg-rule-heavy"
              >
                i
              </button>
              <ArticleCard article={article} />
            </div>
            <div
              className={`${meta ? "translate-x-0" : "translate-x-full"} flex flex-col bg-paper-alt w-[50%] h-[calc(100vh-4rem)] overflow-hidden transition-all duration-500 ease-in-out px-10`}
            >
              <MetaCard
                article={article}
                meta={meta}
                relatedArticles={relatedArticles}
                handleCompare={openCompare}
              />
            </div>
          </div>
          {compareReady && (
            <CompareView
              mainArticle={article}
              offArticle={offArticle}
              mainList={mainList}
              offList={offList}
              handleClose={closeCompare}
            />
          )}
        </div>
      )}
    </>
  );
}

export default ArticleView;
