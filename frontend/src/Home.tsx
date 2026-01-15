import { useState, useEffect } from "react";
import { Link } from "react-router-dom";

type Article = {
  url: String;
  site: String;
  title: String;
  text: String;
  images: String[];
  labels: String;
  score: Number;
  cluster_id: String;
  article_keywords: String[];
};

function Home() {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    const BASE = import.meta.env.BASE_URL;

    async function load() {
      try {
        const res = await fetch(`${BASE}data/articles.json`);
        if (!res.ok) throw new Error(res.statusText);

        const data = await res.json();
        if (!cancelled) setArticles(data);
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
  }, []);

  if (loading) return <div>Loading…</div>;

  return (
    <div className="flex-col bg-paper-main h-[calc(100vh-4rem)] overflow-hidden max-w-[75%] mx-auto">
      <div className="flex content-center justify-center text-[5rem] text-ink-main">
        News Articles
      </div>
      <div className="h-full mx-10 overflow-y-auto no-scrollbar">
        <ul className="text-accent-blue text-[2rem] underline space-y-7">
          {articles.map((article: Article, index) => (
            <li key={index} className="font-bold">
              <Link to={`/article?q=${encodeURIComponent(index)}`}>
                {article.title}
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default Home;
