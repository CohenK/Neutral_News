import MiniPreviewCard from "./MiniPreviewCard";
import Rating from "./Rating";
import type { Article } from "./types";

function MetaCard({
  article,
  meta,
  relatedArticles,
  handleCompare,
}: {
  article: Article;
  meta: boolean;
  relatedArticles: Article[];
  handleCompare: (url: string) => void;
}) {
  return (
    <>
      <div className="text-[2rem] text-ink-main mx-auto">Article Rating:</div>
      <div className="mx-auto">
        <Rating score={article.score} rating={article.labels} toggle={meta} />
      </div>

      <div className="text-[2rem] text-ink-main">Related Articles:</div>
      <div className="flex-1 overflow-y-auto no-scrollbar min-h-0 min-w-0">
        {relatedArticles.length === 0 ? (
          <div className="text-[3rem] text-ink-main text-center">
            No related articles found from our list of news outlets
          </div>
        ) : (
          <ul className="space-y-5">
            {relatedArticles.map((article: Article, index) => (
              <li key={index}>
                <MiniPreviewCard article={article} compare={handleCompare} />
              </li>
            ))}
          </ul>
        )}
      </div>
    </>
  );
}

export default MetaCard;
