import { Outlet } from "react-router-dom";
import type { Article, Pair, Cluster } from "./types";
import { useEffect, useState } from "react";
import "./App.css";
import Navbar from "./Navbar";
import Loading from "./Loading";

function App() {
  const [articles, setArticles] = useState<Article[]>([]);
  const [pairs, setPairs] = useState<Pair[]>([]);
  const [clusters, setClusters] = useState<Cluster>({});
  const [urlMap, setUrlMap] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function init() {
      try {
        let raw_articles = sessionStorage.getItem("articles");
        let raw_pairs = sessionStorage.getItem("pairs");
        let raw_clusters = sessionStorage.getItem("clusters");
        // cache miss
        if (!raw_articles || !raw_pairs || !raw_clusters) {
          const BASE = import.meta.env.BASE_URL;
          const article_file = await fetch(`${BASE}data/articles.json`);
          const pair_file = await fetch(`${BASE}data/pairs.json`);
          const cluster_file = await fetch(`${BASE}data/clusters.json`);
          if (!article_file.ok) throw new Error(article_file.statusText);
          if (!pair_file.ok) throw new Error(pair_file.statusText);
          if (!cluster_file.ok) throw new Error(cluster_file.statusText);

          const article_data = (await article_file.json()) as Article[];
          const pair_data = (await pair_file.json()) as Pair[];
          const cluster_data = (await cluster_file.json()) as Cluster;

          if (cancelled) return;

          setArticles(article_data);
          setPairs(pair_data);
          setClusters(cluster_data);
          sessionStorage.setItem("articles", JSON.stringify(article_data));
          sessionStorage.setItem("pairs", JSON.stringify(pair_data));
          sessionStorage.setItem("clusters", JSON.stringify(cluster_data));

          let url_map = {} as Record<string, string>;
          Object.entries(article_data).forEach(([key, article]) => {
            url_map[article.url] = key;
          });
          setUrlMap(url_map);
          return;
        }
        // cache hit
        const cached_articles = JSON.parse(raw_articles) as Article[];
        const cached_pairs = JSON.parse(raw_pairs!) as Pair[];
        const cached_clusters = JSON.parse(raw_clusters!) as Cluster;
        if (cancelled) return;

        if (cached_articles && cached_articles.length > 0) {
          setArticles(cached_articles);
          setPairs(cached_pairs);
          setClusters(cached_clusters);
          let url_map = {} as Record<string, string>;
          Object.entries(cached_articles).forEach(([key, article]) => {
            url_map[article.url] = key;
          });
          setUrlMap(url_map);
        } else {
          // if articles is empty, then pair and cluster data is useless so set empty for consistency
          setArticles([]);
          setPairs([]);
          setClusters({});
          console.error(
            "Failed to load articles, please try refreshing your browse",
          );
        }
      } catch (err) {
        console.error(
          "Failed to load articles, please try refreshing your browse",
          err,
        );
        sessionStorage.removeItem("articles");
        sessionStorage.removeItem("pairs");
        sessionStorage.removeItem("clusters");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    init();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="flex flex-col min-h-screen font-['Times_New_Roman',Times,serif]">
      <Navbar />
      <div className="flex-1 bg-[url('/NeutralNewsBG.png')] bg-left-top">
        {loading ? (
          <Loading />
        ) : (
          <Outlet context={{ articles, pairs, clusters, urlMap, loading }} />
        )}
      </div>
    </div>
  );
}

export default App;
