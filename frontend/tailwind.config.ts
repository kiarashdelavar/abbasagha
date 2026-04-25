// tailwind.config.ts
import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["var(--font-montserrat)"],
      },
      colors: {
        // تم سایه و مدرن
        background: "#0a0a0a",
        "sidebar-bg": "#141414",
        "item-gray": "#1a1a1a",
        "item-gray-hover": "#242424",
        text: "#ffffff",

        bunq: {
          green: "#41a64f",
          lime: "#74c044",
          cyan: "#31cbd1",
          blue: "#3174c1",
          darkblue: "#2b4b98",
          maroon: "#a63c46",
          red: "#ee3c3c",
          orange: "#ee7c3c",
          yellow: "#fec13c",
        },
      },
    },
  },
  plugins: [],
};
export default config;
