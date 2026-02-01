import { useLocation } from "react-router-dom";
import ArticleView from "./ArticleView";

function KeyedArticleView() {
  const { search } = useLocation();
  return <ArticleView key={search} />;
}

export default KeyedArticleView;
