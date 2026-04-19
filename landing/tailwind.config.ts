import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#0A66C2",
          50: "#E8F4FB",
          100: "#D1E9F7",
          200: "#A3D3EF",
          300: "#75BDE7",
          400: "#3D97D9",
          500: "#0A66C2",
          600: "#085299",
          700: "#063E73",
          800: "#042A4D",
          900: "#021626",
        },
        secondary: {
          DEFAULT: "#00A4BD",
          500: "#00A4BD",
          600: "#008499",
        },
        success: "#57A639",
        warning: "#F5C26B",
        error: "#E74C3C",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      animation: {
        "fade-up": "fadeUp 0.6s ease-out forwards",
        "fade-in": "fadeIn 0.5s ease-out forwards",
        "count-up": "countUp 2s ease-out forwards",
        float: "float 3s ease-in-out infinite",
        "pulse-slow": "pulse 3s ease-in-out infinite",
        gradient: "gradient 8s ease infinite",
      },
      keyframes: {
        fadeUp: {
          "0%": { opacity: "0", transform: "translateY(24px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-8px)" },
        },
        gradient: {
          "0%, 100%": { backgroundPosition: "0% 50%" },
          "50%": { backgroundPosition: "100% 50%" },
        },
      },
      backgroundImage: {
        "grid-pattern":
          "linear-gradient(rgba(10,102,194,0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(10,102,194,0.05) 1px, transparent 1px)",
        "hero-gradient":
          "radial-gradient(ellipse 80% 80% at 50% -20%, rgba(10,102,194,0.15), transparent)",
      },
      backgroundSize: {
        "grid-size": "40px 40px",
      },
      boxShadow: {
        card: "0 1px 3px 0 rgba(0,0,0,0.1), 0 1px 2px -1px rgba(0,0,0,0.1)",
        "card-hover":
          "0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -4px rgba(0,0,0,0.1)",
        glow: "0 0 30px rgba(10,102,194,0.2)",
      },
    },
  },
  plugins: [],
};

export default config;
