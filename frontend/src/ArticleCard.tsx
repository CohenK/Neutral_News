import type { Article } from "./types";

function ArticleCard({
  article,
  match_list,
}: {
  article: Article;
  match_list: string[];
}) {
  return (
    <>
      <div className="flex justify-center text-[3rem] text-ink-main">
        {article.title}
      </div>
      <div className="text-accent-blue text-[1.5rem]">
        News Outlet: {article.site}
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
