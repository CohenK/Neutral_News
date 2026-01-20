import { Outlet } from "react-router-dom";
import type { Article } from "./types";
import { useEffect, useState } from "react";
import "./App.css";
import Navbar from "./Navbar";

function App() {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    const KEY = "articles";

    async function init() {
      try {
        let raw = sessionStorage.getItem(KEY);
        // cache miss
        if (!raw) {
          const BASE = import.meta.env.BASE_URL;
          const res = await fetch(`${BASE}data/articles.json`);
          if (!res.ok) throw new Error(res.statusText);

          const data = (await res.json()) as Article[];

          if (cancelled) return;

          setArticles(data);
          sessionStorage.setItem(KEY, JSON.stringify(data));
          return;
        }
        // cache hit
        const cached = JSON.parse(raw) as Article[];
        if (cancelled) return;

        if (cached && cached.length > 0) {
          setArticles(cached);
        } else {
          setArticles([]);
          console.error(
            "Failed to load articles, please try refreshing your browse"
          );
        }
      } catch (err) {
        console.error(
          "Failed to load articles, please try refreshing your browse",
          err
        );
        sessionStorage.removeItem(KEY);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    init();
    return () => {
      cancelled = true;
    };
  }, []);

  if (loading) return <div>Loading…</div>;

  return (
    <div className="flex flex-col min-h-screen font-['Times_New_Roman',Times,serif]">
      <Navbar />
      <div className="flex-1 bg-[url('/NeutralNewsBG.png')] bg-left-top">
        <Outlet context={{ articles, loading }} />
      </div>
    </div>
  );
}

export default App;
