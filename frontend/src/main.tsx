import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.tsx";
import About from "./about.tsx";
import Disclosure from "./disclosure.tsx";
import NotFound from "./NotFound.tsx";
import Home from "./Home.tsx";
import Article from "./Article.tsx";
import { createBrowserRouter, RouterProvider } from "react-router-dom";

const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    errorElement: <NotFound />,
    children: [
      { index: true, element: <Home /> },
      { path: "about", element: <About /> },
      { path: "disclosure", element: <Disclosure /> },
      { path: "article", element: <Article /> },
    ],
  },
]);

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>
);
