import type { Article } from "./types";

function ArticleCard({
  article,
  match_list,
}: {
  article: Article;
  match_list: string[];
}) {
  const paragraphSplitter = (paragraph: string, targets: string[]) => {
    // use an array to store beginning and ending of sentences, third parameter is 0 for regular strings and 1 for target strings
    let indices: [number, number, number][] = [];
    let start = 0;
    targets.forEach((target) => {
      const beg = paragraph.indexOf(target, start);
      const end = beg + target.length;
      if (beg > start) {
        indices.push([start, beg, 0]);
      }
      indices.push([beg, end, 1]);
      start = end;
    });
    if (start < paragraph.length) {
      indices.push([start, paragraph.length, 0]);
    }
    return indices;
  };

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
