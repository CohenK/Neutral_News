import { useEffect, useState, useRef } from "react";

function Rating({
  score,
  rating,
  toggle,
}: {
  score: number;
  rating: string;
  toggle: boolean;
}) {
  const RADIUS = 10;
  const CIRC = 2 * Math.PI * RADIUS;
  const DURATION = 1500;
  const [value, setValue] = useState<number>(0);
  const [dashoffset, setDashoffset] = useState<number>(0);
  const startValueRef = useRef<number>(score);

  useEffect(() => {
    const progress = CIRC * (1 - score);
    const startValue = 0;
    const startTime = performance.now();

    if (!toggle) {
      setTimeout(() => {
        setDashoffset(CIRC);
        setValue(0);
        startValueRef.current = score;
      }, 500);
      return;
    }

    setDashoffset(CIRC);
    requestAnimationFrame(() => {
      setTimeout(() => {
        setDashoffset(progress);
        requestAnimationFrame(currentScore);
      }, 700);
    });

    function currentScore(time: number) {
      const elapsed = time - startTime;
      const progress = Math.min(elapsed / DURATION, 1);
      const eased = 1 - Math.pow(1 - progress, 3);

      const current = startValue + (score - startValue) * eased;
      setValue(Number(current.toFixed(2)) * 100);

      if (progress < 1) requestAnimationFrame(currentScore);
    }
  }, [toggle]);
  return (
    <>
      <div className="relative ">
        <svg viewBox="0 0 24 24" className="size-50 text-accent-blue mx-2">
          <g transform={`rotate(-90 12 12)`}>
            <circle
              cx="12"
              cy="12"
              r="10"
              fill="none"
              stroke="green"
              strokeWidth="1"
              strokeLinecap="round"
              strokeDasharray={2 * Math.PI * 10}
              strokeDashoffset={dashoffset}
              className="transition-[stroke-dashoffset] duration-1500 cubic-bezier(0,1,1,.72)"
            />
          </g>
        </svg>
        <div className="absolute inset-0 flex flex-col justify-center items-center text-ink-main">
          <div className="text-[3rem]">{rating}</div>
          <div className="text-[1rem]">Confidence: {value}%</div>
        </div>
      </div>
    </>
  );
}

export default Rating;
