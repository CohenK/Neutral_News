import PreviewCard from "./PreviewCard";
import { useOutletContext } from "react-router-dom";
import type { Article, AppCtx } from "./types";
import Loading from "./Loading";

function Home() {
  const { articles, loading } = useOutletContext<AppCtx>();

  return (
    <>
      {loading ? (
        <Loading />
      ) : (
        <div className="flex flex-col bg-paper-main h-[calc(100vh-4rem)] overflow-hidden max-w-[75%] mx-auto">
          <div className="flex content-center justify-center text-[5rem] text-ink-main">
            Daily Articles
          </div>
          <div className="h-full min-h-0 mx-10 overflow-y-auto no-scrollbar">
            <ul className="space-y-7">
              {Object.values(articles).map((article: Article, index) => (
                <li key={index} className="font-bold">
                  <PreviewCard article={article} index={index} />
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </>
  );
}

export default Home;
