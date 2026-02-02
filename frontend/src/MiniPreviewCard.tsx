import type { Article } from "./types";
import { useNavigate } from "react-router-dom";

function MiniPreviewCard({
  article,
  index,
  compare,
}: {
  article: Article;
  index: string;
  compare: (articleID: string) => void;
}) {
  const navigate = useNavigate();
  const handleNavigate = () => {
    navigate(`/article?q=${encodeURIComponent(index)}`);
  };
  const buttonClass =
    "text-[1rem] border border-ink-soft rounded-md px-2 hover:bg-paper-main cursor-pointer hover:text-ink-main";
  return (
    <div>
      <div className="text-[1.5rem] text-accent-blue">{article.title}</div>
      <div className="text-[1rem] text-accent-red">{article.site}</div>
      <div className="text-[1rem] text-ink-soft">
        Bias: {article.labels}, Confidence: {(article.score * 100).toFixed(0)}%
      </div>
      <div className="flex text-ink-faded gap-3">
        <button className={buttonClass} onClick={() => compare(article.url)}>
          compare
        </button>
        <button className={buttonClass} onClick={handleNavigate}>
          navigate
        </button>
      </div>
    </div>
  );
}

export default MiniPreviewCard;
