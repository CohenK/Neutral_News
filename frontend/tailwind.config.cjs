/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        "paper-main": "#F4F1EC",
        "paper-alt": "#EFE6D8",
        "ink-main": "#1F1F1D",
        "ink-soft": "#3A3A36",
        "ink-faded": "#6B6B63",
        "accent-red": "#8B2E2E",
        "accent-blue": "#2F4A5C",
        "rule-light": "#C6BFAF",
        "rule-heavy": "#A8A08E",
      },
    },
  },
  plugins: [],
};
