import { Outlet } from "react-router-dom";
import "./App.css";
import Navbar from "./Navbar";

function App() {
  return (
    <div className="h-[100vh]">
      <Navbar />
      <Outlet />
    </div>
  );
}

export default App;
