import type { Article } from "./types";

function CompareCard({
  article,
  matchList,
  offList,
}: {
  article: Article | undefined;
  matchList: string[];
  offList: string[];
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
      {article ? (
        <div className="flex flex-col h-full min-h-0 bg-paper-main p-10">
          <div className="flex justify-center text-[2rem] text-ink-main underline">
            {article.title}
          </div>
          <div className="flex-1 text-ink-soft text-[1.5rem] text-justify overflow-y-auto no-scrollbar">
            {article.article}
          </div>
        </div>
      ) : (
        ""
      )}
    </>
  );
}

export default CompareCard;
