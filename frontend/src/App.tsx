import { Outlet } from "react-router-dom";
import "./App.css";
import Navbar from "./Navbar";

function App() {
  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />
      <div className="flex-1 bg-[url('/NeutralNewsBG.png')] bg-cover bg-left-top bg-no-repeat">
        <Outlet />
      </div>
    </div>
  );
}

export default App;
