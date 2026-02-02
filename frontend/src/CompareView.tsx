import CompareCard from "./CompareCard";
import type { Article } from "./types";
import { useEffect, useRef } from "react";

function CompareView({
  mainArticle,
  offArticle,
  mainList,
  offList,
  handleClose,
}: {
  mainArticle: Article;
  offArticle: Article | undefined;
  mainList: string[];
  offList: string[];
  handleClose: () => void;
}) {
  useEffect(() => {
    modalRef.current?.focus();
  }, []);

  const compareClasses =
    "relative z-10 w-[45%] h-[80%] min-h-0 pointer-events-auto overflow-hidden rounded-xl";
  const modalRef = useRef<HTMLDivElement>(null);
  return (
    <div
      ref={modalRef}
      tabIndex={-1}
      className="absolute flex justify-around items-center inset-0 z-50 bg-black/80 pointer-events-auto"
      onClick={handleClose}
      onKeyDown={(e) => {
        if (e.key === "Escape") {
          handleClose();
        }
      }}
    >
      <button
        aria-label="Close"
        className="absolute left-5 top-5 text-3xl leading-none text-white border border-1 px-2 rounded-xl hover:bg-paper-main hover:text-ink-main transition"
      >
        ×
      </button>

      <div className={compareClasses} onClick={(e) => e.stopPropagation()}>
        <CompareCard
          article={mainArticle}
          matchList={mainList}
          offList={offList}
        />
      </div>
      <div className={compareClasses} onClick={(e) => e.stopPropagation()}>
        <CompareCard
          article={offArticle}
          matchList={offList}
          offList={mainList}
        />
      </div>
    </div>
  );
}

export default CompareView;
