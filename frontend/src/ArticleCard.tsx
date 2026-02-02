import type { Article } from "./types";

function ArticleCard({ article }: { article: Article }) {
  return (
    <>
      <div className="flex justify-center text-[3rem] text-ink-main">
        {article.title}
      </div>
      <div className="flex text-accent-blue text-[1.5rem] gap-2">
        News Outlet:
        <div className="font-bold">{article.site}</div>
      </div>
      <div className="flex gap-2 text-[1.5rem]">
        <div className="text-accent-blue">Original article:</div>
        <a
          className="text-accent-red underline"
          href={article.url}
          target="_blank"
          rel="noopener noreferrer"
        >
          Link
        </a>
      </div>
      <div className="text-accent-blue text-[1.5rem]">Article:</div>
      <div className="text-ink-soft text-[1.5rem] text-justify overflow-y-auto no-scrollbar min-w-0">
        {article.article}
      </div>
    </>
  );
}

export default ArticleCard;
