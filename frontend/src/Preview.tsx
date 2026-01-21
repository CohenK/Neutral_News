import { Link } from "react-router-dom";
import type { Article } from "./types";

function Preview({ article, index }: { article: Article; index: number }) {
  return (
    <div className="flex-col">
      <div className="text-accent-blue text-[2rem] underline">
        <Link to={`/article?q=${encodeURIComponent(index)}`}>
          {article.title}
        </Link>
      </div>
      <div className="text-accent-red text-[1.5rem]">{article.site}</div>
      <div className="flex flex-wrap gap-3">
        {article.article_keywords.map((keyword: string) => (
          <div key={keyword} className="text-ink-main text-[1rem]">
            [{keyword}]
          </div>
        ))}
      </div>
    </div>
  );
}

export default Preview;
