import { Link } from "react-router-dom";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

function Navbar() {
  const [search, setSearch] = useState("");
  const navigate = useNavigate();
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (search != "") {
      navigate(`/results?q=${encodeURIComponent(search)}`);
    }
    setSearch("");
  };

  return (
    <div className="bg-gray-700 flex items-center justify-between w-full h-[4rem] text-[1.5rem] font-[]">
      <div className="flex mx-3 h-full">
        <Link to={"/"} className="h-full flex items-center">
          <img
            className="h-[80%] w-auto object-contain max-w-full"
            src={`${import.meta.env.BASE_URL}NeutralNewsLogo.png`}
            alt=""
          />
        </Link>
      </div>
      <div className="flex flex-1 justify-center items-center h-full">
        <form
          className="flex h-[60%] rounded-full overflow-hidden"
          onSubmit={handleSearch}
        >
          <input
            className="h-full flex-1 px-[1rem] bg-[white] text-black text-lg"
            type="search"
            placeholder="Search"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <button className="h-full flex px-2 bg-gray-400" type="submit">
            <img
              className="w-auto object-contain max-w-full max-h-full"
              src={`${import.meta.env.BASE_URL}SearchIcon.png`}
              alt=""
            />
          </button>
        </form>
      </div>
      <div className="flex items-center mx-3 h-full">
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
