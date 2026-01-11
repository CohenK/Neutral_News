import { useSearchParams } from "react-router-dom";

function Article() {
  const [searchParams] = useSearchParams();
  const query = searchParams.get("q");

  return (
    <>
      <div>{query}</div>
    </>
  );
}

export default Article;
