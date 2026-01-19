import { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import type { Article } from "./types";
import Preview from "./Preview";

function Results() {
  const [searchParams] = useSearchParams();
  const query = searchParams.get("q");
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    let cancelled = false;
    const BASE = import.meta.env.BASE_URL;

    async function load() {
      try {
        const res = await fetch(`${BASE}data/articles.json`);
        if (!res.ok) throw new Error(res.statusText);

        const data = await res.json();

        if (!cancelled) {
          const filtered = data.filter(
            (d: Article) =>
              d.title.toLowerCase().includes(query!.toLowerCase()) ||
              d.article.toLowerCase().includes(query!.toLowerCase())
          );
          setArticles(filtered);
        }
      } catch (err) {
        console.error("Failed to load articles", err);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [query]);

  if (loading) return <div>Loading…</div>;

  return (
    <div className="flex flex-col bg-paper-main h-[calc(100vh-4rem)] overflow-hidden max-w-[75%] mx-auto">
      <div className="flex content-center justify-start text-[3rem] text-ink-main mx-10">
        Results for: "{query}"
      </div>
      <div className="min-h-0 mx-10 overflow-y-auto no-scrollbar">
        <ul className="space-y-7">
          {articles.map((article: Article, index) => (
            <li key={index} className="font-bold">
              <Preview article={article} index={index} />
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default Results;
