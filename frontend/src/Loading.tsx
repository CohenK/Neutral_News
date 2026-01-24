function Loading() {
  return (
    <div className="flex items-center justify-center mx-auto">
      <svg
        viewBox="0 0 24 24"
        className="size-6 text-accent-blue animate-spin mx-2"
      >
        <circle
          cx="12"
          cy="12"
          r="10"
          fill="none"
          stroke="currentColor"
          strokeWidth="4"
          strokeLinecap="round"
          strokeDasharray="31.4"
          strokeDashoffset="10"
        />
      </svg>
      <div className="text-ink-main text-[1.5rem]">Loading…</div>
    </div>
  );
}

export default Loading;
