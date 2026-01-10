import { Link } from "react-router-dom";

function Navbar() {
  return (
    <div className="bg-gray-700 flex items-center justify-between w-full h-[3rem] text-[1.5rem] ">
      <div className="flex mx-3 h-full">
        <Link to={"/"} className="h-full flex items-center">
          <img
            className="h-[80%] w-auto object-contain max-w-full"
            src="/public/Neutral News Logo.png"
            alt=""
          />
        </Link>
      </div>
      <div className="flex mx-3 h-full">
        <Link className="mx-3" to={"/about"}>
          About
        </Link>
        <Link className="mx-3" to={"/disclosure"}>
          Disclosures
        </Link>
      </div>
    </div>
  );
}

export default Navbar;
