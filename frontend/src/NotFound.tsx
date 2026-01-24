import Navbar from "./Navbar";

function NotFound() {
  return (
    <div className="flex flex-col min-h-screen font-['Times_New_Roman',Times,serif]">
      <Navbar />
      <div className="flex-1 bg-[url('/NeutralNewsBG.png')] bg-left-top">
        <div className="flex justify-center items-center bg-paper-main text-ink-main text-[3rem] h-[calc(100vh-4rem)] max-w-[75%] mx-auto">
          404 - Page Not Found
        </div>
      </div>
    </div>
  );
}

export default NotFound;
