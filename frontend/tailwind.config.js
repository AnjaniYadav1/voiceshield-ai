/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        void: "#0B0F14",
        panel: "#121821",
        panel2: "#182230",
        line: "#233040",
        signal: "#4FD8E8",
        safe: "#3DDC97",
        warn: "#F5A623",
        danger: "#FF5470",
        ink: "#E7EDF3",
        inkdim: "#8CA0B3",
      },
      fontFamily: {
        display: ["'Space Grotesk'", "sans-serif"],
        body: ["'Inter'", "sans-serif"],
        mono: ["'JetBrains Mono'", "monospace"],
      },
      boxShadow: {
        glow: "0 0 24px -4px rgba(79, 216, 232, 0.35)",
      },
    },
  },
  plugins: [],
};
