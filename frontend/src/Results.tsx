import { useState, useEffect } from "react";
import { useSearchParams, useOutletContext } from "react-router-dom";
import type { Article, AppCtx } from "./types";
import Preview from "./PreviewCard";
import { Link } from "react-router-dom";

function Results() {
  const [searchParams] = useSearchParams();
  const query = searchParams.get("q");
  const { articles, loading } = useOutletContext<AppCtx>();
  const [results, setResults] = useState<Article[]>([]);

  useEffect(() => {
    const filtered = Object.values(articles).filter(
      (a: Article) =>
        a.title.toLowerCase().includes(query!.toLowerCase()) ||
        a.article.toLowerCase().includes(query!.toLowerCase()),
    );
    setResults(filtered);

    return () => {};
  }, [query]);

  if (loading) return <div>Loading…</div>;

  return (
    <div className="flex flex-col bg-paper-main h-[calc(100vh-4rem)] overflow-hidden max-w-[75%] mx-auto px-10">
      <div className="text-[3rem] text-ink-main">Results for: "{query}"</div>
      <div className="text-accent-blue text-[1.25rem] my-2">
        <Link className="py-1 px-2 border" to={"/"}>
          &lt;&lt;&lt; All Articles
        </Link>
      </div>

      <div className="min-h-0 overflow-y-auto no-scrollbar">
        <ul className="space-y-7">
          {results.map((article: Article, index) => (
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
