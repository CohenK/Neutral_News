import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.tsx";
import About from "./About.tsx";
import Disclosure from "./Disclosure.tsx";
import NotFound from "./NotFound.tsx";
import Home from "./Home.tsx";
import KeyedArticleView from "./KeyedArticleView.tsx";
import Results from "./Results.tsx";
import { createHashRouter, RouterProvider } from "react-router-dom";

const router = createHashRouter([
  {
    path: "/",
    element: <App />,
    errorElement: <NotFound />,
    children: [
      { index: true, element: <Home /> },
      { path: "results", element: <Results /> },
      { path: "article", element: <KeyedArticleView /> },
      { path: "about", element: <About /> },
      { path: "disclosure", element: <Disclosure /> },
    ],
  },
]);

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>,
);
